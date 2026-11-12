"""Board presets and application colour themes (chess.com inspired)."""

BOARD_THEMES = {
    'Green': ('#EEEED2', '#769656'),
    'Brown': ('#F0D9B5', '#B58863'),
    'Walnut': ('#E8D0A9', '#A0703F'),
    'Blue': ('#DEE3E6', '#6B8EAD'),
    'Ice': ('#E8F1F8', '#8CB2D1'),
    'Purple': ('#E8DFF5', '#9277B5'),
    'Coral': ('#F7E3D3', '#D9776B'),
    'Sand': ('#F5ECD0', '#C9A66B'),
    'Tournament': ('#FFFFFF', '#5C8A5A'),
    'Gray': ('#E5E7EB', '#64748B'),
    'Midnight': ('#8A94A6', '#2F3A4F'),
    'Dark': ('#AEB7C2', '#394554'),
    'Neon': ('#2C2F4A', '#14162A'),
    'Marble': ('#E9E6E1', '#9A9A9F'),
}

# name: bg, panel, panel2 (cards), text, muted, accent, accent_dark, border, input
UI_THEMES = {
    'Chess.com Dark': dict(bg='#302e2b', panel='#262522', panel2='#3a3835', text='#ffffff', muted='#a3a19f',
                           accent='#81b64c', accent_dark='#5d8a36', border='#454340', input='#262522', nav='#262522'),
    'Midnight Blue': dict(bg='#1b2430', panel='#151c26', panel2='#243042', text='#f1f5f9', muted='#94a3b8',
                          accent='#4aa3ff', accent_dark='#2b7fd4', border='#33445c', input='#151c26', nav='#151c26'),
    'Light': dict(bg='#f1f3f5', panel='#ffffff', panel2='#e9edf0', text='#20252d', muted='#6b7683',
                  accent='#6fa33b', accent_dark='#4f7d28', border='#d4dae0', input='#ffffff', nav='#ffffff'),
}


def build_stylesheet(t):
    return '''
QMainWindow, QDialog { background:%(bg)s; }
QWidget { color:%(text)s; font-size:14px; }
QWidget#pageRoot, QStackedWidget { background:%(bg)s; }
QFrame#panel { background:%(panel)s; border-radius:10px; }
QFrame#card { background:%(panel2)s; border-radius:10px; border:2px solid transparent; }
QFrame#card:hover { border:2px solid %(border)s; }
QFrame#cardSelected { background:%(panel2)s; border-radius:10px; border:2px solid %(accent)s; }
QFrame#nav { background:%(nav)s; }
QFrame#introCard { background:%(panel)s; }
QLabel { background:transparent; }
QLabel#stripName { font-weight:bold; font-size:15px; }
QLabel#stripRating { color:%(muted)s; font-size:13px; }
QLabel#pageTitle { font-size:26px; font-weight:800; }
QLabel#muted { color:%(muted)s; }
QPushButton { background:%(panel2)s; color:%(text)s; border:0; border-radius:8px; padding:9px 14px; font-weight:600; }
QPushButton:hover { background:%(border)s; }
QPushButton:disabled { color:%(muted)s; background:%(panel)s; }
QPushButton#primary { background:%(accent)s; color:#ffffff; border-bottom:4px solid %(accent_dark)s; font-size:16px; font-weight:800; padding:12px 18px; }
QPushButton#primary:hover { background:%(accent)s; border-bottom:4px solid %(accent_dark)s; }
QPushButton#primary:disabled { background:%(border)s; border-bottom:4px solid %(panel)s; color:%(muted)s; }
QPushButton#navButton { background:transparent; text-align:left; padding:12px 16px; font-size:15px; border-radius:8px; color:%(muted)s; }
QPushButton#navButton:hover { background:%(panel2)s; color:%(text)s; }
QPushButton#navButtonActive { background:%(panel2)s; text-align:left; padding:12px 16px; font-size:15px; border-radius:8px; color:%(text)s; }
QPushButton#sideChoice { background:%(panel2)s; border:2px solid transparent; padding:10px 6px; }
QPushButton#sideChoice:checked { border:2px solid %(accent)s; background:%(panel)s; }
QToolButton#pieceButton { background:%(panel2)s; border:2px solid transparent; border-radius:8px; color:%(muted)s; font-size:11px; }
QToolButton#pieceButton:checked { border:2px solid %(accent)s; background:%(panel)s; color:%(text)s; }
QToolButton#pieceButton:hover { border:2px solid %(border)s; }
QComboBox, QSpinBox, QLineEdit { background:%(input)s; color:%(text)s; border:1px solid %(border)s; border-radius:6px; padding:7px; }
QComboBox QAbstractItemView { background:%(panel)s; color:%(text)s; selection-background-color:%(accent)s; selection-color:#ffffff; }
QListWidget, QTableWidget { background:%(panel)s; color:%(text)s; border:0; border-radius:8px; outline:0; }
QListWidget::item { padding:6px; border-radius:6px; }
QListWidget::item:selected, QTableWidget::item:selected { background:%(panel2)s; color:%(text)s; }
QHeaderView::section { background:%(panel)s; color:%(muted)s; border:0; padding:6px; font-weight:bold; }
QTableWidget { gridline-color:transparent; alternate-background-color:%(panel)s; }
QScrollArea { border:0; background:transparent; }
QScrollBar:vertical { background:transparent; width:10px; }
QScrollBar::handle:vertical { background:%(border)s; border-radius:5px; min-height:30px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0; }
QGroupBox { border:1px solid %(border)s; border-radius:10px; margin-top:14px; padding:14px 10px 10px 10px; font-weight:bold; }
QGroupBox::title { subcontrol-origin:margin; left:12px; padding:0 6px; color:%(muted)s; }
QTabWidget::pane { border:0; }
QTabBar::tab { background:%(panel)s; color:%(muted)s; padding:10px 18px; border-top-left-radius:8px; border-top-right-radius:8px; margin-right:3px; }
QTabBar::tab:selected { background:%(panel2)s; color:%(text)s; }
QCheckBox { spacing:8px; }
QSlider::groove:horizontal { height:6px; background:%(border)s; border-radius:3px; }
QSlider::handle:horizontal { background:%(accent)s; width:16px; margin:-5px 0; border-radius:8px; }
QProgressBar { background:%(panel)s; border:0; border-radius:6px; height:12px; text-align:center; }
QProgressBar::chunk { background:%(accent)s; border-radius:6px; }
QMenu { background:%(panel)s; color:%(text)s; border:1px solid %(border)s; }
QMenu::item:selected { background:%(accent)s; }
QToolTip { background:%(panel)s; color:%(text)s; border:1px solid %(border)s; }
QStatusBar { background:%(nav)s; color:%(muted)s; }
''' % t
