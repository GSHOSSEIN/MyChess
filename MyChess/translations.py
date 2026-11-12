"""UI translations. Format per line:  English ¦ Español ¦ Français ¦ Deutsch ¦ Português ¦ Italiano
Anything missing falls back to English, so you can add or fix lines freely."""

_RAW = """
Play ¦ Jugar ¦ Jouer ¦ Spielen ¦ Jogar ¦ Gioca
Bots ¦ Bots ¦ Bots ¦ Bots ¦ Bots ¦ Bot
LAN ¦ LAN ¦ LAN ¦ LAN ¦ LAN ¦ LAN
Friends ¦ Amigos ¦ Amis ¦ Freunde ¦ Amigos ¦ Amici
History ¦ Historial ¦ Historique ¦ Verlauf ¦ Histórico ¦ Cronologia
Settings ¦ Ajustes ¦ Paramètres ¦ Einstellungen ¦ Configurações ¦ Impostazioni
Play Chess ¦ Jugar al ajedrez ¦ Jouer aux échecs ¦ Schach spielen ¦ Jogar xadrez ¦ Gioca a scacchi
Your chess game, your rules. ¦ Tu ajedrez, tus reglas. ¦ Vos échecs, vos règles. ¦ Dein Schach, deine Regeln. ¦ Seu xadrez, suas regras. ¦ I tuoi scacchi, le tue regole.
Time control ¦ Control de tiempo ¦ Cadence ¦ Bedenkzeit ¦ Controle de tempo ¦ Controllo del tempo
No limit ¦ Sin límite ¦ Sans limite ¦ Unbegrenzt ¦ Sem limite ¦ Nessun limite
Play Bots ¦ Jugar contra bots ¦ Jouer contre des bots ¦ Gegen Bots spielen ¦ Jogar contra bots ¦ Gioca contro i bot
Play a Friend (LAN) ¦ Jugar con un amigo (LAN) ¦ Jouer avec un ami (LAN) ¦ Gegen Freund spielen (LAN) ¦ Jogar com um amigo (LAN) ¦ Gioca con un amico (LAN)
Pass & Play ¦ Dos jugadores local ¦ Deux joueurs local ¦ Lokal zu zweit ¦ Dois jogadores local ¦ Due giocatori locale
Player 2 ¦ Jugador 2 ¦ Joueur 2 ¦ Spieler 2 ¦ Jogador 2 ¦ Giocatore 2
Review a game (PGN) ¦ Analizar una partida (PGN) ¦ Analyser une partie (PGN) ¦ Partie analysieren (PGN) ¦ Analisar uma partida (PGN) ¦ Analizza una partita (PGN)
Recent games ¦ Partidas recientes ¦ Parties récentes ¦ Letzte Partien ¦ Partidas recentes ¦ Partite recenti
Record: {w} W / {d} D / {l} L ¦ Récord: {w} G / {d} E / {l} P ¦ Bilan : {w} V / {d} N / {l} D ¦ Bilanz: {w} S / {d} U / {l} N ¦ Retrospecto: {w} V / {d} E / {l} D ¦ Record: {w} V / {d} P / {l} S
White ¦ Blancas ¦ Blancs ¦ Weiß ¦ Brancas ¦ Bianco
Black ¦ Negras ¦ Noirs ¦ Schwarz ¦ Pretas ¦ Nero
Resign ¦ Rendirse ¦ Abandonner ¦ Aufgeben ¦ Desistir ¦ Abbandona
Draw ¦ Tablas ¦ Nulle ¦ Remis ¦ Empate ¦ Patta
Undo ¦ Deshacer ¦ Annuler ¦ Zurück ¦ Desfazer ¦ Annulla
Flip ¦ Girar ¦ Retourner ¦ Drehen ¦ Girar ¦ Ruota
Rules ¦ Reglas ¦ Règles ¦ Regeln ¦ Regras ¦ Regole
Game Review ¦ Revisión de partida ¦ Analyse de la partie ¦ Partieanalyse ¦ Revisão da partida ¦ Revisione partita
Save PGN ¦ Guardar PGN ¦ Enregistrer PGN ¦ PGN speichern ¦ Salvar PGN ¦ Salva PGN
New game ¦ Nueva partida ¦ Nouvelle partie ¦ Neues Spiel ¦ Novo jogo ¦ Nuova partita
Add friend ¦ Añadir amigo ¦ Ajouter un ami ¦ Freund hinzufügen ¦ Adicionar amigo ¦ Aggiungi amico
Rematch ¦ Revancha ¦ Revanche ¦ Rückspiel ¦ Revanche ¦ Rivincita
Close ¦ Cerrar ¦ Fermer ¦ Schließen ¦ Fechar ¦ Chiudi
Game over ¦ Fin de la partida ¦ Partie terminée ¦ Spiel beendet ¦ Fim de jogo ¦ Partita finita
You won! ¦ ¡Has ganado! ¦ Vous avez gagné ! ¦ Du hast gewonnen! ¦ Você venceu! ¦ Hai vinto!
You lost ¦ Has perdido ¦ Vous avez perdu ¦ Du hast verloren ¦ Você perdeu ¦ Hai perso
Play vs {name} ¦ Jugar contra {name} ¦ Jouer contre {name} ¦ Gegen {name} spielen ¦ Jogar contra {name} ¦ Gioca contro {name}
LAN game ¦ Partida LAN ¦ Partie LAN ¦ LAN-Spiel ¦ Jogo LAN ¦ Partita LAN
{side} to move ¦ Mueven las {side} ¦ Trait aux {side} ¦ {side} am Zug ¦ Vez das {side} ¦ Muove il {side}
{side} wins ¦ Ganan las {side} ¦ Les {side} gagnent ¦ {side} gewinnt ¦ {side} vencem ¦ Vince il {side}
CHECK ¦ JAQUE ¦ ÉCHEC ¦ SCHACH ¦ XEQUE ¦ SCACCO
{name} is thinking… ¦ {name} está pensando… ¦ {name} réfléchit… ¦ {name} denkt nach… ¦ {name} está pensando… ¦ {name} sta pensando…
by checkmate ¦ por jaque mate ¦ par échec et mat ¦ durch Schachmatt ¦ por xeque-mate ¦ per scacco matto
by stalemate ¦ por ahogado ¦ par pat ¦ durch Patt ¦ por afogamento ¦ per stallo
by insufficient material ¦ por material insuficiente ¦ par matériel insuffisant ¦ wegen unzureichenden Materials ¦ por material insuficiente ¦ per materiale insufficiente
by the 50-move rule ¦ por la regla de 50 movimientos ¦ par la règle des 50 coups ¦ nach der 50-Züge-Regel ¦ pela regra dos 50 lances ¦ per la regola delle 50 mosse
by threefold repetition ¦ por triple repetición ¦ par triple répétition ¦ durch dreifache Stellungswiederholung ¦ por tripla repetição ¦ per triplice ripetizione
by resignation ¦ por abandono ¦ par abandon ¦ durch Aufgabe ¦ por desistência ¦ per abbandono
on time ¦ por tiempo ¦ au temps ¦ durch Zeitüberschreitung ¦ por tempo ¦ per tempo
by agreement ¦ por acuerdo ¦ par accord mutuel ¦ durch Einigung ¦ por acordo ¦ per accordo
because the opponent disconnected ¦ porque el rival se desconectó ¦ car l'adversaire s'est déconnecté ¦ weil der Gegner die Verbindung verlor ¦ porque o oponente desconectou ¦ perché l'avversario si è disconnesso
Are you sure you want to resign? ¦ ¿Seguro que quieres rendirte? ¦ Voulez-vous vraiment abandonner ? ¦ Willst du wirklich aufgeben? ¦ Tem certeza de que deseja desistir? ¦ Sei sicuro di voler abbandonare?
Viewing move {n} of {total} ¦ Viendo la jugada {n} de {total} ¦ Coup {n} sur {total} ¦ Zug {n} von {total} ¦ Vendo o lance {n} de {total} ¦ Mossa {n} di {total}
premove set ¦ jugada previa lista ¦ premove prêt ¦ Vorzug gesetzt ¦ pré-lance definido ¦ premossa impostata
MATCH STARTING ¦ COMIENZA LA PARTIDA ¦ LA PARTIE COMMENCE ¦ SPIEL BEGINNT ¦ A PARTIDA VAI COMEÇAR ¦ LA PARTITA INIZIA
Starting in {n}…  (click to skip) ¦ Empieza en {n}…  (clic para saltar) ¦ Début dans {n}…  (clic pour passer) ¦ Start in {n}…  (Klick zum Überspringen) ¦ Começa em {n}…  (clique para pular) ¦ Inizio tra {n}…  (clic per saltare)
Highlight square ¦ Resaltar casilla ¦ Surligner la case ¦ Feld markieren ¦ Destacar casa ¦ Evidenzia casa
Mark as No Capture ¦ Marcar como No Captura ¦ Marquer comme non capturable ¦ Als nicht schlagbar markieren ¦ Marcar como sem captura ¦ Segna come non catturabile
Remove No Capture ¦ Quitar No Captura ¦ Retirer non capturable ¦ Nicht-schlagbar entfernen ¦ Remover sem captura ¦ Rimuovi non catturabile
Waiting for the other player… ¦ Esperando al otro jugador… ¦ En attente de l'autre joueur… ¦ Warte auf den anderen Spieler… ¦ Aguardando o outro jogador… ¦ In attesa dell'altro giocatore…
Custom pieces & rules ¦ Piezas y reglas personalizadas ¦ Pièces et règles personnalisées ¦ Eigene Figuren & Regeln ¦ Peças e regras personalizadas ¦ Pezzi e regole personalizzati
1. Pick the pieces you want to change (you can select several) ¦ 1. Elige las piezas que quieres cambiar (puedes elegir varias) ¦ 1. Choisissez les pièces à modifier (plusieurs possibles) ¦ 1. Wähle die Figuren, die du ändern willst (mehrere möglich) ¦ 1. Escolha as peças que quer mudar (pode escolher várias) ¦ 1. Scegli i pezzi da modificare (anche più di uno)
2. Choose how they move ¦ 2. Elige cómo se mueven ¦ 2. Choisissez comment elles se déplacent ¦ 2. Wähle, wie sie ziehen ¦ 2. Escolha como elas se movem ¦ 2. Scegli come si muovono
All white ¦ Todas las blancas ¦ Tous les blancs ¦ Alle weißen ¦ Todas as brancas ¦ Tutti i bianchi
All black ¦ Todas las negras ¦ Tous les noirs ¦ Alle schwarzen ¦ Todas as pretas ¦ Tutti i neri
Everything ¦ Todas ¦ Toutes ¦ Alle ¦ Todas ¦ Tutti
Clear selection ¦ Borrar selección ¦ Effacer la sélection ¦ Auswahl löschen ¦ Limpar seleção ¦ Cancella selezione
Standard (normal chess) ¦ Estándar (ajedrez normal) ¦ Standard (échecs normaux) ¦ Standard (normales Schach) ¦ Padrão (xadrez normal) ¦ Standard (scacchi normali)
Standard ¦ Estándar ¦ Standard ¦ Standard ¦ Padrão ¦ Standard
Queen movement ¦ Movimiento de dama ¦ Déplacement de dame ¦ Damenzug ¦ Movimento de dama ¦ Movimento di donna
Rook movement ¦ Movimiento de torre ¦ Déplacement de tour ¦ Turmzug ¦ Movimento de torre ¦ Movimento di torre
Bishop movement ¦ Movimiento de alfil ¦ Déplacement de fou ¦ Läuferzug ¦ Movimento de bispo ¦ Movimento di alfiere
Knight movement ¦ Movimiento de caballo ¦ Déplacement de cavalier ¦ Springerzug ¦ Movimento de cavalo ¦ Movimento di cavallo
Pawn: up to 4 forward ¦ Peón: hasta 4 casillas ¦ Pion : jusqu'à 4 cases ¦ Bauer: bis zu 4 vor ¦ Peão: até 4 casas ¦ Pedone: fino a 4 avanti
Move anywhere ¦ Mover a cualquier casilla ¦ Aller n'importe où ¦ Überallhin ziehen ¦ Mover para qualquer casa ¦ Muovi ovunque
No Capture: ¦ No Captura: ¦ Non capturable : ¦ Nicht schlagbar: ¦ Sem captura: ¦ Non catturabile:
Don't change ¦ No cambiar ¦ Ne pas changer ¦ Nicht ändern ¦ Não alterar ¦ Non cambiare
Protect these pieces on the board ¦ Proteger estas piezas en el tablero ¦ Protéger ces pièces sur l'échiquier ¦ Diese Figuren auf dem Brett schützen ¦ Proteger estas peças no tabuleiro ¦ Proteggi questi pezzi sulla scacchiera
Remove protection ¦ Quitar protección ¦ Retirer la protection ¦ Schutz entfernen ¦ Remover proteção ¦ Rimuovi protezione
Active rules ¦ Reglas activas ¦ Règles actives ¦ Aktive Regeln ¦ Regras ativas ¦ Regole attive
Apply ¦ Aplicar ¦ Appliquer ¦ Anwenden ¦ Aplicar ¦ Applica
Reset selected ¦ Restablecer selección ¦ Réinitialiser la sélection ¦ Auswahl zurücksetzen ¦ Redefinir seleção ¦ Ripristina selezione
Reset all rules ¦ Restablecer todas las reglas ¦ Réinitialiser toutes les règles ¦ Alle Regeln zurücksetzen ¦ Redefinir todas as regras ¦ Ripristina tutte le regole
Select at least one piece first. ¦ Elige al menos una pieza primero. ¦ Choisissez d'abord au moins une pièce. ¦ Wähle zuerst mindestens eine Figur. ¦ Escolha pelo menos uma peça primeiro. ¦ Scegli prima almeno un pezzo.
Applied. ¦ Aplicado. ¦ Appliqué. ¦ Angewendet. ¦ Aplicado. ¦ Applicato.
All rules reset to standard chess. ¦ Todas las reglas restablecidas al ajedrez estándar. ¦ Toutes les règles sont revenues aux échecs standard. ¦ Alle Regeln auf Standardschach zurückgesetzt. ¦ Todas as regras voltaram ao xadrez padrão. ¦ Tutte le regole ripristinate agli scacchi standard.
King ¦ Rey ¦ Roi ¦ König ¦ Rei ¦ Re
Queen ¦ Dama ¦ Dame ¦ Dame ¦ Dama ¦ Donna
Rook ¦ Torre ¦ Tour ¦ Turm ¦ Torre ¦ Torre
Bishop ¦ Alfil ¦ Fou ¦ Läufer ¦ Bispo ¦ Alfiere
Knight ¦ Caballo ¦ Cavalier ¦ Springer ¦ Cavalo ¦ Cavallo
Pawn ¦ Peón ¦ Pion ¦ Bauer ¦ Peão ¦ Pedone
king ¦ rey ¦ roi ¦ König ¦ rei ¦ re
queen ¦ dama ¦ dame ¦ Dame ¦ dama ¦ donna
rook ¦ torre ¦ tour ¦ Turm ¦ torre ¦ torre
bishop ¦ alfil ¦ fou ¦ Läufer ¦ bispo ¦ alfiere
knight ¦ caballo ¦ cavalier ¦ Springer ¦ cavalo ¦ cavallo
pawn ¦ peón ¦ pion ¦ Bauer ¦ peão ¦ pedone
Play as ¦ Jugar con ¦ Jouer les ¦ Spielen als ¦ Jogar de ¦ Gioca come
Random ¦ Aleatorio ¦ Aléatoire ¦ Zufällig ¦ Aleatório ¦ Casuale
Play ¦ Jugar ¦ Jouer ¦ Spielen ¦ Jogar ¦ Gioca
Beginner ¦ Principiante ¦ Débutant ¦ Anfänger ¦ Iniciante ¦ Principiante
Intermediate ¦ Intermedio ¦ Intermédiaire ¦ Fortgeschritten ¦ Intermediário ¦ Intermedio
Advanced ¦ Avanzado ¦ Avancé ¦ Erfahren ¦ Avançado ¦ Avanzato
Master ¦ Maestro ¦ Maître ¦ Meister ¦ Mestre ¦ Maestro
Engine ¦ Motor ¦ Moteur ¦ Engine ¦ Motor ¦ Motore
Easy ¦ Fácil ¦ Facile ¦ Leicht ¦ Fácil ¦ Facile
Medium ¦ Medio ¦ Moyen ¦ Mittel ¦ Médio ¦ Medio
Hard ¦ Difícil ¦ Difficile ¦ Schwer ¦ Difícil ¦ Difficile
Maximum ¦ Máximo ¦ Maximum ¦ Maximal ¦ Máximo ¦ Massimo
Stockfish level ¦ Nivel de Stockfish ¦ Niveau de Stockfish ¦ Stockfish-Stufe ¦ Nível do Stockfish ¦ Livello di Stockfish
Host a game ¦ Crear partida ¦ Héberger une partie ¦ Spiel hosten ¦ Criar partida ¦ Ospita una partita
Join a game ¦ Unirse a una partida ¦ Rejoindre une partie ¦ Spiel beitreten ¦ Entrar numa partida ¦ Unisciti a una partita
Port ¦ Puerto ¦ Port ¦ Port ¦ Porta ¦ Porta
You play ¦ Juegas con ¦ Vous jouez les ¦ Du spielst ¦ Você joga de ¦ Giochi con
Host game ¦ Crear partida ¦ Héberger ¦ Hosten ¦ Criar partida ¦ Ospita
Stop hosting ¦ Dejar de alojar ¦ Arrêter l'hébergement ¦ Hosten beenden ¦ Parar de hospedar ¦ Smetti di ospitare
Join ¦ Unirse ¦ Rejoindre ¦ Beitreten ¦ Entrar ¦ Unisciti
Join selected game ¦ Unirse a la partida elegida ¦ Rejoindre la partie choisie ¦ Gewähltem Spiel beitreten ¦ Entrar na partida escolhida ¦ Unisciti alla partita scelta
Copy ¦ Copiar ¦ Copier ¦ Kopieren ¦ Copiar ¦ Copia
Your address: ¦ Tu dirección: ¦ Votre adresse : ¦ Deine Adresse: ¦ Seu endereço: ¦ Il tuo indirizzo:
Games on your network appear here automatically: ¦ Las partidas de tu red aparecen aquí automáticamente: ¦ Les parties de votre réseau apparaissent ici automatiquement : ¦ Spiele in deinem Netzwerk erscheinen hier automatisch: ¦ As partidas da sua rede aparecem aqui automaticamente: ¦ Le partite nella tua rete compaiono qui automaticamente:
No games found yet… ¦ Aún no hay partidas… ¦ Aucune partie trouvée… ¦ Noch keine Spiele gefunden… ¦ Nenhuma partida encontrada… ¦ Nessuna partita trovata…
Challenge ¦ Retar ¦ Défier ¦ Herausfordern ¦ Desafiar ¦ Sfida
Remove friend ¦ Eliminar amigo ¦ Retirer l'ami ¦ Freund entfernen ¦ Remover amigo ¦ Rimuovi amico
Save address ¦ Guardar dirección ¦ Enregistrer l'adresse ¦ Adresse speichern ¦ Salvar endereço ¦ Salva indirizzo
No friends yet ¦ Aún no tienes amigos ¦ Pas encore d'amis ¦ Noch keine Freunde ¦ Ainda sem amigos ¦ Ancora nessun amico
hosting now ¦ alojando ahora ¦ héberge en ce moment ¦ hostet gerade ¦ hospedando agora ¦ sta ospitando
Match History ¦ Historial de partidas ¦ Historique des parties ¦ Partienverlauf ¦ Histórico de partidas ¦ Cronologia partite
Date ¦ Fecha ¦ Date ¦ Datum ¦ Data ¦ Data
Opponent ¦ Rival ¦ Adversaire ¦ Gegner ¦ Oponente ¦ Avversario
Color ¦ Color ¦ Couleur ¦ Farbe ¦ Cor ¦ Colore
Result ¦ Resultado ¦ Résultat ¦ Ergebnis ¦ Resultado ¦ Risultato
Moves ¦ Jugadas ¦ Coups ¦ Züge ¦ Lances ¦ Mosse
Mode ¦ Modo ¦ Mode ¦ Modus ¦ Modo ¦ Modalità
Win ¦ Victoria ¦ Victoire ¦ Sieg ¦ Vitória ¦ Vittoria
Loss ¦ Derrota ¦ Défaite ¦ Niederlage ¦ Derrota ¦ Sconfitta
Delete ¦ Eliminar ¦ Supprimer ¦ Löschen ¦ Excluir ¦ Elimina
Export PGN ¦ Exportar PGN ¦ Exporter PGN ¦ PGN exportieren ¦ Exportar PGN ¦ Esporta PGN
Bot ¦ Bot ¦ Bot ¦ Bot ¦ Bot ¦ Bot
Profile ¦ Perfil ¦ Profil ¦ Profil ¦ Perfil ¦ Profilo
Appearance ¦ Apariencia ¦ Apparence ¦ Aussehen ¦ Aparência ¦ Aspetto
Game ¦ Juego ¦ Jeu ¦ Spiel ¦ Jogo ¦ Gioco
Username ¦ Nombre de usuario ¦ Nom d'utilisateur ¦ Benutzername ¦ Nome de usuário ¦ Nome utente
Upload profile picture… ¦ Subir foto de perfil… ¦ Importer une photo de profil… ¦ Profilbild hochladen… ¦ Enviar foto de perfil… ¦ Carica foto del profilo…
…or pick an avatar: ¦ …o elige un avatar: ¦ …ou choisissez un avatar : ¦ …oder wähle einen Avatar: ¦ …ou escolha um avatar: ¦ …oppure scegli un avatar:
Reset Elo to 800 ¦ Restablecer Elo a 800 ¦ Remettre l'Elo à 800 ¦ Elo auf 800 zurücksetzen ¦ Redefinir Elo para 800 ¦ Reimposta Elo a 800
Language ¦ Idioma ¦ Langue ¦ Sprache ¦ Idioma ¦ Lingua
App theme ¦ Tema de la app ¦ Thème de l'application ¦ App-Design ¦ Tema do app ¦ Tema dell'app
Board theme ¦ Tema del tablero ¦ Thème de l'échiquier ¦ Brett-Design ¦ Tema do tabuleiro ¦ Tema della scacchiera
Piece set ¦ Juego de piezas ¦ Jeu de pièces ¦ Figurensatz ¦ Conjunto de peças ¦ Set di pezzi
Light squares… ¦ Casillas claras… ¦ Cases claires… ¦ Helle Felder… ¦ Casas claras… ¦ Caselle chiare…
Dark squares… ¦ Casillas oscuras… ¦ Cases sombres… ¦ Dunkle Felder… ¦ Casas escuras… ¦ Caselle scure…
Custom ¦ Personalizado ¦ Personnalisé ¦ Benutzerdefiniert ¦ Personalizado ¦ Personalizzato
Move sounds ¦ Sonidos de jugada ¦ Sons des coups ¦ Zugsounds ¦ Sons de lances ¦ Suoni delle mosse
Volume ¦ Volumen ¦ Volume ¦ Lautstärke ¦ Volume ¦ Volume
Piece animations ¦ Animaciones de piezas ¦ Animations des pièces ¦ Figuren-Animationen ¦ Animações das peças ¦ Animazioni dei pezzi
Show legal move dots ¦ Mostrar puntos de jugadas legales ¦ Afficher les coups légaux ¦ Legale Züge anzeigen ¦ Mostrar lances legais ¦ Mostra le mosse legali
Show board coordinates ¦ Mostrar coordenadas ¦ Afficher les coordonnées ¦ Koordinaten anzeigen ¦ Mostrar coordenadas ¦ Mostra le coordinate
Choose Stockfish executable… ¦ Elegir ejecutable de Stockfish… ¦ Choisir l'exécutable Stockfish… ¦ Stockfish-Programm wählen… ¦ Escolher executável do Stockfish… ¦ Scegli l'eseguibile di Stockfish…
Show best move ¦ Mostrar mejor jugada ¦ Montrer le meilleur coup ¦ Besten Zug zeigen ¦ Mostrar melhor lance ¦ Mostra la mossa migliore
Back ¦ Volver ¦ Retour ¦ Zurück ¦ Voltar ¦ Indietro
Summary ¦ Resumen ¦ Résumé ¦ Zusammenfassung ¦ Resumo ¦ Riepilogo
Accuracy ¦ Precisión ¦ Précision ¦ Genauigkeit ¦ Precisão ¦ Precisione
Brilliant ¦ Brillante ¦ Brillant ¦ Brillant ¦ Brilhante ¦ Brillante
Great ¦ Muy buena ¦ Très bon ¦ Sehr gut ¦ Ótimo ¦ Ottima
Best ¦ Mejor ¦ Meilleur ¦ Bester ¦ Melhor ¦ Migliore
Excellent ¦ Excelente ¦ Excellent ¦ Exzellent ¦ Excelente ¦ Eccellente
Good ¦ Buena ¦ Bon ¦ Gut ¦ Boa ¦ Buona
Book ¦ Teoría ¦ Théorie ¦ Eröffnungsbuch ¦ Teoria ¦ Teoria
Forced ¦ Forzada ¦ Forcé ¦ Erzwungen ¦ Forçado ¦ Forzata
Inaccuracy ¦ Imprecisión ¦ Imprécision ¦ Ungenauigkeit ¦ Imprecisão ¦ Imprecisione
Mistake ¦ Error ¦ Erreur ¦ Fehler ¦ Erro ¦ Errore
Miss ¦ Oportunidad perdida ¦ Occasion manquée ¦ Verpasst ¦ Oportunidade perdida ¦ Occasione persa
Blunder ¦ Error grave ¦ Gaffe ¦ Patzer ¦ Erro grave ¦ Errore grave
{san} is the best move. ¦ {san} es la mejor jugada. ¦ {san} est le meilleur coup. ¦ {san} ist der beste Zug. ¦ {san} é o melhor lance. ¦ {san} è la mossa migliore.
{san} is a good move. ¦ {san} es una buena jugada. ¦ {san} est un bon coup. ¦ {san} ist ein guter Zug. ¦ {san} é um bom lance. ¦ {san} è una buona mossa.
{san} is an excellent move. ¦ {san} es una jugada excelente. ¦ {san} est un excellent coup. ¦ {san} ist ein exzellenter Zug. ¦ {san} é um lance excelente. ¦ {san} è un'ottima mossa.
{san} is a book move. ¦ {san} es jugada de teoría. ¦ {san} est un coup de théorie. ¦ {san} ist ein Buchzug. ¦ {san} é um lance de teoria. ¦ {san} è una mossa di teoria.
{san} is an inaccuracy. ¦ {san} es una imprecisión. ¦ {san} est une imprécision. ¦ {san} ist eine Ungenauigkeit. ¦ {san} é uma imprecisão. ¦ {san} è un'imprecisione.
{san} is a mistake. ¦ {san} es un error. ¦ {san} est une erreur. ¦ {san} ist ein Fehler. ¦ {san} é um erro. ¦ {san} è un errore.
{san} is a blunder. ¦ {san} es un error grave. ¦ {san} est une gaffe. ¦ {san} ist ein Patzer. ¦ {san} é um erro grave. ¦ {san} è un errore grave.
{san} is brilliant! A bold sacrifice that really works. ¦ ¡{san} es brillante! Un sacrificio audaz que funciona. ¦ {san} est brillant ! Un sacrifice audacieux qui fonctionne. ¦ {san} ist brillant! Ein mutiges Opfer, das funktioniert. ¦ {san} é brilhante! Um sacrifício ousado que funciona. ¦ {san} è brillante! Un sacrificio audace che funziona.
{san} is checkmate! Well played. ¦ ¡{san} es jaque mate! Bien jugado. ¦ {san} est mat ! Bien joué. ¦ {san} ist Schachmatt! Gut gespielt. ¦ {san} é xeque-mate! Bem jogado. ¦ {san} è scacco matto! Ben giocato.
{san} misses a chance to take advantage. ¦ {san} desaprovecha una oportunidad. ¦ {san} manque une occasion. ¦ {san} verpasst eine Chance. ¦ {san} perde uma oportunidade. ¦ {san} spreca un'occasione.
{best} was better. ¦ {best} era mejor. ¦ {best} était meilleur. ¦ {best} war besser. ¦ {best} era melhor. ¦ {best} era meglio.
Analysis complete. ¦ Análisis completo. ¦ Analyse terminée. ¦ Analyse abgeschlossen. ¦ Análise concluída. ¦ Analisi completata.
Let me take a look at the game… ¦ Déjame revisar la partida… ¦ Laissez-moi regarder la partie… ¦ Ich sehe mir die Partie an… ¦ Deixe-me analisar a partida… ¦ Do un'occhiata alla partita…
Analysis done! Use the arrows to step through the game. ¦ ¡Análisis listo! Usa las flechas para recorrer la partida. ¦ Analyse prête ! Utilisez les flèches pour parcourir la partie. ¦ Analyse fertig! Mit den Pfeilen durch die Partie gehen. ¦ Análise pronta! Use as setas para percorrer a partida. ¦ Analisi pronta! Usa le frecce per scorrere la partita.
Rematch requested… ¦ Revancha solicitada… ¦ Revanche demandée… ¦ Rückspiel angefragt… ¦ Revanche solicitada… ¦ Rivincita richiesta…
Draw offer sent… ¦ Oferta de tablas enviada… ¦ Offre de nulle envoyée… ¦ Remisangebot gesendet… ¦ Oferta de empate enviada… ¦ Offerta di patta inviata…
Your opponent offers a draw. Accept? ¦ Tu rival ofrece tablas. ¿Aceptas? ¦ Votre adversaire propose nulle. Accepter ? ¦ Dein Gegner bietet Remis an. Annehmen? ¦ Seu oponente oferece empate. Aceitar? ¦ Il tuo avversario offre patta. Accetti?
Do both players agree to a draw? ¦ ¿Ambos jugadores aceptan tablas? ¦ Les deux joueurs acceptent-ils la nulle ? ¦ Sind beide Spieler mit Remis einverstanden? ¦ Ambos os jogadores aceitam o empate? ¦ Entrambi i giocatori accettano la patta?
Connecting to {host}:{port}… ¦ Conectando con {host}:{port}… ¦ Connexion à {host}:{port}… ¦ Verbinde mit {host}:{port}… ¦ Conectando a {host}:{port}… ¦ Connessione a {host}:{port}…
Waiting for a player to join…  {ip}:{port} ¦ Esperando a que se una un jugador…  {ip}:{port} ¦ En attente d'un joueur…  {ip}:{port} ¦ Warte auf einen Mitspieler…  {ip}:{port} ¦ Aguardando um jogador…  {ip}:{port} ¦ In attesa di un giocatore…  {ip}:{port}
Connected. Setting up the game… ¦ Conectado. Preparando la partida… ¦ Connecté. Préparation de la partie… ¦ Verbunden. Spiel wird vorbereitet… ¦ Conectado. Preparando a partida… ¦ Connesso. Preparazione della partita…
Opponent disconnected ¦ El rival se desconectó ¦ L'adversaire s'est déconnecté ¦ Gegner hat die Verbindung getrennt ¦ O oponente desconectou ¦ L'avversario si è disconnesso
Opponent left the game ¦ El rival abandonó la partida ¦ L'adversaire a quitté la partie ¦ Gegner hat das Spiel verlassen ¦ O oponente saiu do jogo ¦ L'avversario ha lasciato la partita
Connection lost ¦ Conexión perdida ¦ Connexion perdue ¦ Verbindung verloren ¦ Conexão perdida ¦ Connessione persa
{name} wants to add you as a friend. Accept? ¦ {name} quiere añadirte como amigo. ¿Aceptas? ¦ {name} veut vous ajouter comme ami. Accepter ? ¦ {name} möchte dich als Freund hinzufügen. Annehmen? ¦ {name} quer adicionar você como amigo. Aceitar? ¦ {name} vuole aggiungerti come amico. Accetti?
{name} is now your friend. ¦ {name} ahora es tu amigo. ¦ {name} est maintenant votre ami. ¦ {name} ist jetzt dein Freund. ¦ {name} agora é seu amigo. ¦ {name} ora è tuo amico.
Friend request sent. ¦ Solicitud de amistad enviada. ¦ Demande d'ami envoyée. ¦ Freundschaftsanfrage gesendet. ¦ Pedido de amizade enviado. ¦ Richiesta di amicizia inviata.
Game review needs standard chess rules. ¦ La revisión necesita reglas de ajedrez estándar. ¦ L'analyse nécessite les règles standard. ¦ Die Analyse braucht Standardregeln. ¦ A revisão precisa de regras padrão. ¦ La revisione richiede le regole standard.
Hint ¦ Pista ¦ Indice ¦ Tipp ¦ Dica ¦ Suggerimento
Thinking of a hint… ¦ Pensando una pista… ¦ Recherche d'un indice… ¦ Suche einen Tipp… ¦ Pensando numa dica… ¦ Cerco un suggerimento…
Hint: try {move}  (this game is now unrated) ¦ Pista: prueba {move}  (esta partida ya no puntúa) ¦ Indice : essayez {move}  (cette partie n'est plus classée) ¦ Tipp: versuche {move}  (diese Partie wird nicht gewertet) ¦ Dica: tente {move}  (esta partida não vale pontos) ¦ Suggerimento: prova {move}  (questa partita non è più valida per l'Elo)
Starting position ¦ Posición inicial ¦ Position de départ ¦ Grundstellung ¦ Posição inicial ¦ Posizione iniziale
Bot starts without its queen ¦ El bot empieza sin su dama ¦ Le bot commence sans sa dame ¦ Der Bot startet ohne Dame ¦ O bot começa sem a dama ¦ Il bot parte senza donna
Bot starts without a rook ¦ El bot empieza sin una torre ¦ Le bot commence sans une tour ¦ Der Bot startet ohne Turm ¦ O bot começa sem uma torre ¦ Il bot parte senza una torre
Bot starts without a bishop ¦ El bot empieza sin un alfil ¦ Le bot commence sans un fou ¦ Der Bot startet ohne Läufer ¦ O bot começa sem um bispo ¦ Il bot parte senza un alfiere
Bot starts without a knight ¦ El bot empieza sin un caballo ¦ Le bot commence sans un cavalier ¦ Der Bot startet ohne Springer ¦ O bot começa sem um cavalo ¦ Il bot parte senza un cavallo
I start without my queen ¦ Empiezo sin mi dama ¦ Je commence sans ma dame ¦ Ich starte ohne Dame ¦ Eu começo sem a dama ¦ Parto senza donna
I start without a rook ¦ Empiezo sin una torre ¦ Je commence sans une tour ¦ Ich starte ohne Turm ¦ Eu começo sem uma torre ¦ Parto senza una torre
I start without a knight ¦ Empiezo sin un caballo ¦ Je commence sans un cavalier ¦ Ich starte ohne Springer ¦ Eu começo sem um cavalo ¦ Parto senza un cavallo
Sound pack ¦ Paquete de sonidos ¦ Pack de sons ¦ Soundpaket ¦ Pacote de sons ¦ Pacchetto suoni
Stats ¦ Estadísticas ¦ Statistiques ¦ Statistiken ¦ Estatísticas ¦ Statistiche
Games ¦ Partidas ¦ Parties ¦ Partien ¦ Partidas ¦ Partite
Win rate ¦ % de victorias ¦ Taux de victoire ¦ Siegquote ¦ Taxa de vitórias ¦ % di vittorie
Wins / Draws / Losses ¦ Victorias / Tablas / Derrotas ¦ Victoires / Nulles / Défaites ¦ Siege / Remis / Niederlagen ¦ Vitórias / Empates / Derrotas ¦ Vittorie / Patte / Sconfitte
Peak Elo ¦ Elo máximo ¦ Elo maximum ¦ Höchste Elo ¦ Elo máximo ¦ Elo massimo
Best win streak ¦ Mejor racha ¦ Meilleure série ¦ Beste Siegesserie ¦ Melhor sequência ¦ Miglior serie
Elo progress ¦ Progreso de Elo ¦ Progression Elo ¦ Elo-Verlauf ¦ Progresso do Elo ¦ Andamento Elo
Achievements ¦ Logros ¦ Succès ¦ Erfolge ¦ Conquistas ¦ Obiettivi
Play a few rated games to see your progress. ¦ Juega algunas partidas puntuadas para ver tu progreso. ¦ Jouez quelques parties classées pour voir votre progression. ¦ Spiele einige gewertete Partien, um deinen Fortschritt zu sehen. ¦ Jogue algumas partidas valendo pontos para ver seu progresso. ¦ Gioca qualche partita valida per vedere i tuoi progressi.
First Win ¦ Primera victoria ¦ Première victoire ¦ Erster Sieg ¦ Primeira vitória ¦ Prima vittoria
Win your first game ¦ Gana tu primera partida ¦ Gagnez votre première partie ¦ Gewinne deine erste Partie ¦ Ganhe sua primeira partida ¦ Vinci la tua prima partita
Play 10 games ¦ Juega 10 partidas ¦ Jouez 10 parties ¦ Spiele 10 Partien ¦ Jogue 10 partidas ¦ Gioca 10 partite
Win 3 games in a row ¦ Gana 3 partidas seguidas ¦ Gagnez 3 parties d'affilée ¦ Gewinne 3 Partien in Folge ¦ Ganhe 3 partidas seguidas ¦ Vinci 3 partite di fila
Win a game as Black ¦ Gana una partida con negras ¦ Gagnez une partie avec les noirs ¦ Gewinne eine Partie mit Schwarz ¦ Ganhe uma partida de pretas ¦ Vinci una partita con il nero
Draw a game ¦ Empata una partida ¦ Faites match nul ¦ Spiele ein Remis ¦ Empate uma partida ¦ Pareggia una partita
Add a friend ¦ Añade un amigo ¦ Ajoutez un ami ¦ Füge einen Freund hinzu ¦ Adicione um amigo ¦ Aggiungi un amico
Puzzles ¦ Problemas ¦ Problèmes ¦ Aufgaben ¦ Quebra-cabeças ¦ Problemi
Learn ¦ Aprender ¦ Apprendre ¦ Lernen ¦ Aprender ¦ Impara
Positions ¦ Posiciones ¦ Positions ¦ Stellungen ¦ Posições ¦ Posizioni
Lessons ¦ Lecciones ¦ Leçons ¦ Lektionen ¦ Lições ¦ Lezioni
Coach ¦ Entrenador ¦ Coach ¦ Trainer ¦ Treinador ¦ Allenatore
Next ¦ Siguiente ¦ Suivant ¦ Weiter ¦ Próximo ¦ Avanti
Finish ¦ Terminar ¦ Terminer ¦ Fertig ¦ Concluir ¦ Fine
Show me ¦ Muéstrame ¦ Montre-moi ¦ Zeig es mir ¦ Mostre ¦ Mostrami
Show solution ¦ Ver solución ¦ Voir la solution ¦ Lösung zeigen ¦ Ver solução ¦ Mostra soluzione
Skip ¦ Saltar ¦ Passer ¦ Überspringen ¦ Pular ¦ Salta
Next puzzle ¦ Siguiente problema ¦ Problème suivant ¦ Nächste Aufgabe ¦ Próximo desafio ¦ Prossimo problema
All puzzles ¦ Todos los problemas ¦ Tous les problèmes ¦ Alle Aufgaben ¦ Todos os desafios ¦ Tutti i problemi
Mate in 1 ¦ Mate en 1 ¦ Mat en 1 ¦ Matt in 1 ¦ Mate em 1 ¦ Matto in 1
Mate in 2 ¦ Mate en 2 ¦ Mat en 2 ¦ Matt in 2 ¦ Mate em 2 ¦ Matto in 2
Find the checkmate! ¦ ¡Encuentra el jaque mate! ¦ Trouvez le mat ! ¦ Finde das Schachmatt! ¦ Encontre o xeque-mate! ¦ Trova lo scacco matto!
Now deliver checkmate! ¦ ¡Ahora da jaque mate! ¦ Maintenant, donnez le mat ! ¦ Jetzt setze matt! ¦ Agora dê o xeque-mate! ¦ Ora dai scacco matto!
White to move ¦ Juegan blancas ¦ Trait aux blancs ¦ Weiß am Zug ¦ Brancas jogam ¦ Muove il bianco
Black to move ¦ Juegan negras ¦ Trait aux noirs ¦ Schwarz am Zug ¦ Pretas jogam ¦ Muove il nero
Custom positions ¦ Posiciones personalizadas ¦ Positions personnalisées ¦ Eigene Stellungen ¦ Posições personalizadas ¦ Posizioni personalizzate
Clear ¦ Vaciar ¦ Vider ¦ Leeren ¦ Limpar ¦ Svuota
Start position ¦ Posición inicial ¦ Position initiale ¦ Grundstellung ¦ Posição inicial ¦ Posizione iniziale
Presets… ¦ Preajustes… ¦ Préréglages… ¦ Vorlagen… ¦ Predefinições… ¦ Preimpostazioni…
Load FEN ¦ Cargar FEN ¦ Charger FEN ¦ FEN laden ¦ Carregar FEN ¦ Carica FEN
Save ¦ Guardar ¦ Enregistrer ¦ Speichern ¦ Salvar ¦ Salva
Load ¦ Cargar ¦ Charger ¦ Laden ¦ Carregar ¦ Carica
Side to move ¦ Turno ¦ Trait ¦ Am Zug ¦ Vez de ¦ Tocca a
Play this position ¦ Jugar esta posición ¦ Jouer cette position ¦ Diese Stellung spielen ¦ Jogar esta posição ¦ Gioca questa posizione
Play from this position ¦ Jugar desde esta posición ¦ Jouer depuis cette position ¦ Ab dieser Stellung spielen ¦ Jogar desta posição ¦ Gioca da questa posizione
Position is valid. ¦ La posición es válida. ¦ La position est valide. ¦ Die Stellung ist gültig. ¦ A posição é válida. ¦ La posizione è valida.
I play White ¦ Juego con blancas ¦ Je joue les blancs ¦ Ich spiele Weiß ¦ Jogo de brancas ¦ Gioco col bianco
I play Black ¦ Juego con negras ¦ Je joue les noirs ¦ Ich spiele Schwarz ¦ Jogo de pretas ¦ Gioco col nero
Live coach tips ¦ Consejos del entrenador en vivo ¦ Conseils du coach en direct ¦ Live-Trainertipps ¦ Dicas do treinador ao vivo ¦ Consigli dal vivo dell'allenatore
Auto-flip board for each player ¦ Girar tablero para cada jugador ¦ Retourner l'échiquier pour chaque joueur ¦ Brett für jeden Spieler drehen ¦ Girar tabuleiro para cada jogador ¦ Ruota la scacchiera per ogni giocatore
Your coach: {name} ¦ Tu entrenador: {name} ¦ Votre coach : {name} ¦ Dein Trainer: {name} ¦ Seu treinador: {name} ¦ Il tuo allenatore: {name}
Tip of the day: ¦ Consejo del día: ¦ Conseil du jour : ¦ Tipp des Tages: ¦ Dica do dia: ¦ Consiglio del giorno:
Archbishop (bishop + knight) ¦ Arzobispo (alfil + caballo) ¦ Archevêque (fou + cavalier) ¦ Erzbischof (Läufer + Springer) ¦ Arcebispo (bispo + cavalo) ¦ Arcivescovo (alfiere + cavallo)
Amazon (queen + knight) ¦ Amazona (dama + caballo) ¦ Amazone (dame + cavalier) ¦ Amazone (Dame + Springer) ¦ Amazona (dama + cavalo) ¦ Amazzone (donna + cavallo)
Chancellor (rook + knight) ¦ Canciller (torre + caballo) ¦ Chancelier (tour + cavalier) ¦ Kanzler (Turm + Springer) ¦ Chanceler (torre + cavalo) ¦ Cancelliere (torre + cavallo)
"""

TRANSLATIONS = {}
_CODES = ['es', 'fr', 'de', 'pt', 'it']
for _line in _RAW.strip().splitlines():
    _parts = [p.strip() for p in _line.split('¦')]
    if len(_parts) != 6:
        continue
    for _code, _text in zip(_CODES, _parts[1:]):
        TRANSLATIONS.setdefault(_code, {})[_parts[0]] = _text
