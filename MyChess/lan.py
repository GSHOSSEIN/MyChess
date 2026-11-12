"""LAN play for My Chess (Qt-free; talks to the GUI through a queue).

Events put on `events` (poll it from a QTimer):
  ('connected', {'addr': ip, 'role': 'host'|'client'})
  ('msg', dict)
  ('closed', reason_text)
  ('error', text)
  ('found', {'host','port','name','rating','id','seen'})      from discovery
Protocol: one JSON object per line over TCP.
"""
import json
import queue
import select
import socket
import threading
import time

DEFAULT_PORT = 8765
DISCOVERY_PORT = 8766
PROTOCOL = 2
MAX_LINE = 4 * 1024 * 1024
KEEPALIVE_EVERY = 4.0
DEAD_AFTER = 20.0


def get_lan_ip():
    """IPv4 address other computers on the local network can use."""
    probe = None
    try:
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        probe.connect(('192.0.2.1', 9))          # selects the route; sends nothing
        address = probe.getsockname()[0]
        if address and not address.startswith('127.'):
            return address
    except OSError:
        pass
    finally:
        if probe:
            probe.close()
    try:
        for item in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            address = item[4][0]
            if not address.startswith('127.') and not address.startswith('169.254.'):
                return address
    except OSError:
        pass
    return ''


def _broadcast_addresses():
    addrs = ['255.255.255.255']
    ip = get_lan_ip()
    if ip:
        parts = ip.split('.')
        if len(parts) == 4:
            addrs.append('.'.join(parts[:3] + ['255']))
    return addrs


class LanSession:
    """One TCP connection to one opponent (either hosting or joining)."""

    def __init__(self):
        self.events = queue.Queue()
        self.sock = None
        self.server = None
        self.role = None
        self.peer_ip = ''
        self.port = DEFAULT_PORT
        self._stop = threading.Event()
        self._send_lock = threading.Lock()
        self._last_rx = time.monotonic()
        self._broadcast_info = None

    # ----------------------------------------------------------- lifecycle
    @property
    def connected(self):
        return self.sock is not None

    def close(self, notify_peer=True):
        self._stop.set()
        if notify_peer and self.sock is not None:
            try:
                self.send({'t': 'bye'})
            except Exception:
                pass
        for obj in (self.sock, self.server):
            try:
                if obj is not None:
                    obj.close()
            except OSError:
                pass
        self.sock = None
        self.server = None
        self.role = None

    # ----------------------------------------------------------------- host
    def host(self, port, info):
        """Start listening (and announcing on the LAN). Raises OSError if the port is taken."""
        self.close(notify_peer=False)
        self._stop = threading.Event()
        self.role = 'host'
        self.port = int(port)
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind(('0.0.0.0', self.port))
            server.listen(1)
        except OSError:
            server.close()
            self.role = None
            raise
        server.settimeout(0.5)
        self.server = server
        self._broadcast_info = dict(info, app='MyChess', port=self.port)
        stop = self._stop
        threading.Thread(target=self._accept_loop, args=(server, stop), daemon=True).start()
        threading.Thread(target=self._announce_loop, args=(stop,), daemon=True).start()

    def _accept_loop(self, server, stop):
        while not stop.is_set():
            try:
                conn, addr = server.accept()
            except socket.timeout:
                continue
            except OSError:
                return
            try:
                server.close()
            except OSError:
                pass
            self.server = None
            self._attach(conn, addr[0], 'host', stop)
            return

    def _announce_loop(self, stop):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            payload = json.dumps(self._broadcast_info).encode('utf-8')
            while not stop.is_set() and self.sock is None:
                for a in _broadcast_addresses():
                    try:
                        sock.sendto(payload, (a, DISCOVERY_PORT))
                    except OSError:
                        pass
                stop.wait(1.0)
        finally:
            sock.close()

    # ----------------------------------------------------------------- join
    def join(self, host, port):
        """Connect in the background (never blocks the GUI)."""
        self.close(notify_peer=False)
        self._stop = threading.Event()
        self.role = 'client'
        self.port = int(port)
        stop = self._stop

        def work():
            try:
                conn = socket.create_connection((host, int(port)), timeout=6)
            except OSError as e:
                if not stop.is_set():
                    self.events.put(('error', 'Could not connect to {}:{} ({})'.format(host, port, e)))
                return
            if stop.is_set():
                conn.close()
                return
            self._attach(conn, host, 'client', stop)

        threading.Thread(target=work, daemon=True).start()

    # ------------------------------------------------------------ messaging
    def _attach(self, conn, ip, role, stop):
        conn.settimeout(None)
        try:
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            conn.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        except OSError:
            pass
        self.sock = conn
        self.peer_ip = ip
        self._last_rx = time.monotonic()
        self.events.put(('connected', {'addr': ip, 'role': role}))
        threading.Thread(target=self._reader, args=(conn, stop), daemon=True).start()
        threading.Thread(target=self._keepalive, args=(conn, stop), daemon=True).start()

    def send(self, obj):
        sock = self.sock
        if sock is None:
            return False
        data = (json.dumps(obj, separators=(',', ':')) + '\n').encode('utf-8')
        try:
            with self._send_lock:
                sock.sendall(data)
            return True
        except OSError as e:
            self._drop(sock, 'Connection lost ({})'.format(e))
            return False

    def _drop(self, sock, reason):
        if self.sock is sock and sock is not None:
            self.sock = None
            try:
                sock.close()
            except OSError:
                pass
            self.events.put(('closed', reason))

    def _reader(self, sock, stop):
        buf = b''
        while not stop.is_set():
            try:
                ready, _, _ = select.select([sock], [], [], 1.0)
                if not ready:
                    continue
                data = sock.recv(65536)
            except (OSError, ValueError):
                self._drop(sock, 'Connection lost')
                return
            if not data:
                self._drop(sock, 'Opponent disconnected')
                return
            self._last_rx = time.monotonic()
            buf += data
            if len(buf) > MAX_LINE:
                self._drop(sock, 'Protocol error')
                return
            while b'\n' in buf:
                line, buf = buf.split(b'\n', 1)
                try:
                    msg = json.loads(line.decode('utf-8'))
                except ValueError:
                    continue
                if not isinstance(msg, dict):
                    continue
                t = msg.get('t')
                if t == 'ping':
                    self.send({'t': 'pong'})
                elif t == 'pong':
                    pass
                elif t == 'bye':
                    self._drop(sock, 'Opponent left the game')
                    return
                else:
                    self.events.put(('msg', msg))

    def _keepalive(self, sock, stop):
        while not stop.wait(KEEPALIVE_EVERY):
            if self.sock is not sock:
                return
            if time.monotonic() - self._last_rx > DEAD_AFTER:
                self._drop(sock, 'Connection timed out')
                return
            self.send({'t': 'ping'})


class Discovery:
    """Listens for hosts announcing themselves on the LAN."""

    def __init__(self, events):
        self.events = events
        self._stop = threading.Event()
        self.thread = None

    def start(self):
        if self.thread is not None:
            return
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self._stop.set()

    def _run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if hasattr(socket, 'SO_REUSEPORT'):
                try:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                except OSError:
                    pass
            sock.bind(('', DISCOVERY_PORT))
            sock.settimeout(1.0)
        except OSError:
            sock.close()
            return
        try:
            while not self._stop.is_set():
                try:
                    data, addr = sock.recvfrom(8192)
                except socket.timeout:
                    continue
                except OSError:
                    return
                try:
                    info = json.loads(data.decode('utf-8'))
                except ValueError:
                    continue
                if not isinstance(info, dict) or info.get('app') != 'MyChess':
                    continue
                self.events.put(('found', {'host': addr[0], 'port': int(info.get('port', DEFAULT_PORT)),
                                           'name': str(info.get('name', '?'))[:24], 'rating': info.get('rating'),
                                           'id': info.get('id', ''), 'tc': info.get('tc', ''), 'seen': time.monotonic()}))
        finally:
            sock.close()
