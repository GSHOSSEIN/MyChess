MY CHESS  -  1.0.0 
==========================================
Features
  * Drag fix: if you pick up a piece while the opponent is still moving, it now stays in your hand and the move works.
  * Chess.com-style layout: left menu, player bars with avatar / name / Elo / captured pieces / clocks, move list, navigation arrows (or keyboard arrows).
  * Match-start card (avatars, names, Elo, "VS") before every game.
  * Profiles: username, Elo (changes after rated games), profile picture (upload one or pick an avatar). Settings > Profile.
  * Bots page: 15 bots from Zach (100) to Viktor (2500) + Stockfish with 4 levels. Pictures are in assets/profiles/bots - replace any PNG with a real picture using the same file name.
  * Game Review: coach with speech bubble, ratings (Brilliant, Great, Best, Excellent, Good, Book, Inaccuracy, Mistake, Miss, Blunder), evaluation bar + graph, accuracy %, best-move arrow, summary table.
    It uses Stockfish when found; otherwise a basic built-in engine.  (Not available for games with house rules.)
  * Friends + Match History: add a friend during a LAN game; friends are saved with their last address; history lists every game with Elo change and can be reviewed/exported.
  * LAN rewritten: automatic discovery of hosted games on the network, handshake (names/Elo/pictures), synced clocks, house rules synced, disconnect detection, rematch, no UI freezing while connecting.
  * Promotion picker appears on the board like chess.com (Queen, Knight, Rook, Bishop, X to cancel).
  * Custom pieces & rules (Rules button): pick pieces by their pictures (several at once), choose movement, Apply / Reset selected / Reset all rules.
    New movement style "Move anywhere" (no move dots; these pieces never give check).  Pawns with house rules can now promote to any piece.
  * Themes: 14 board colour presets, 3 app themes, 7 piece sets (Classic = yours, plus Glyph, Neon, Gold & Silver, Wooden, Ocean, Tokens).
    Your own piece set: make a folder in assets/piece_sets with wP.png wN.png wB.png wR.png wQ.png wK.png and bP.png ... bK.png.
  * Languages: English, Español, Français, Deutsch, Português, Italiano (translations.py - add or fix lines freely).
  * Sounds (move, capture, check, castle, promote, start, end), time controls (1+0 ... 30 min, with increments), draw offers, resign, threefold/50-move/insufficient-material draws.
  * Faster: bot thinking and game review run in background threads, board background is cached, move generation is cached, Stockfish has no console window flash.

New Features
  * Premove promotion: when you premove a pawn onto the last rank the promotion picker appears right away, so you choose the piece.
  * Menus are readable in every theme (the whole app now follows the dark/light palette, including scroll areas, tabs and pop-ups).
  * New illustrated bot / avatar portraits (shaded faces, hair, glasses, hats, a chess piece behind each character).
    They are original drawings - chess.com's own artwork and sounds are copyrighted and cannot be bundled. Replace any PNG in assets/profiles/bots with your own picture (same file name).
  * Sounds: new wooden "tock" sounds, plus a second pack ("Digital"). Settings > Game > Sound pack.
    To use your own sounds: create a folder inside assets/sounds (for example assets/sounds/MyPack) and put WAV files named
    move.wav capture.wav castle.wav check.wav promote.wav start.wav end.wav notify.wav lowtime.wav in it. It then shows up in the Sound pack list.
  * New features: Hint button (Stockfish shows a best-move arrow; the game becomes unrated),
    Odds games on the Bots page (start without a queen / rook / bishop / knight - for you or the bot),
    Stats tab in History (win rate, record, peak Elo, win streak, Elo graph) and 13 Achievements.

More coachs
  * Coaches: Levy, Magnus, Hikaru, Botez Sisters, David, Dr. Wolf and Mittens. Pick yours in Settings > Coach (that is the only place to change it).
    The coach appears on the Home page (tip of the day), in Lessons, Puzzles, Game Review and as live tips in bot games (checkbox in the game panel).
    Comment lines are generic coaching text in a tone that fits each coach - they are not quotes from the real people.
  * Every coach is also a bot (Bots > Coach) playing at about their Elo. The Elo numbers are my estimates - edit coaches.py to change them.
  * Learn: 6 interactive lessons (pieces, checkmate, castling incl. LONG castling, en passant, tactics, openings, endgames).
  * Puzzles: 100 verified puzzles (50 mate-in-1, 50 mate-in-2) with a puzzle rating and streak. Regenerate with tools/mine_puzzles.py.
  * Positions: set up any position (drag pieces, presets, FEN, save your own), then play it vs a bot or with a friend.
  * Rules menu: new AMAZON (queen + knight), ARCHBISHOP (bishop + knight) and CHANCELLOR (rook + knight). Pieces with house-rule movement show a small purple letter.
  * Pass & Play flips the board for each player (checkbox in the game panel / Settings).
  * Long castling: you can now also click or drag the king onto the rook to castle. (If long castling still fails in some position, tell me the position.)
  * Review: your brilliant / great / best / excellent / good / book / inaccuracy / mistake / miss / blunder pictures are used on the board, move list and summary.
  * New piece set "Cburnett" (added next to the others - nothing replaced). Pieces by Colin M.L. Burnett, CC BY-SA 3.0 (Wikimedia Commons).
  * Your sounds: the MP3s were converted to WAV and are the default pack ("Your sounds"): move, opponent move, capture, check, castle, promote, premove, start, end, notify, 10 seconds.

LAN HOW-TO
  Host: Play a Friend (LAN) > Host game.   Friend: the game appears in "Join a game" automatically (or type the host IP).
  Both PCs must be on the same network. Allow My Chess through Windows Firewall (Private networks) if asked.
  If the game does not appear automatically, type the host's IPv4 address (shown on the Host card) and port 8765.

CONTROLS
  Click or drag pieces. Premove: select a piece while it's the opponent's turn. Right-drag = arrows (Shift red, Ctrl yellow, Alt blue).
  Right-click = highlight square.  Ctrl + right-click on a piece = toggle No Capture for that piece.
  Arrow keys = browse moves.

