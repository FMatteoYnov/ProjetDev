from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
import sqlite3
import threading

app = Flask(__name__)
app.secret_key = "votre_cle_secrete"
socketio = SocketIO(app, cors_allowed_origins="*")

waiting_players = []  # [(sid, pseudo)]
sid_to_pseudo = {}
sid_to_ip = {}

DB_PATH = "matchmaking.db"

# === Utilitaires DB ===
def insert_in_file(pseudo, ip):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO file_attente (pseudo, ip, port) VALUES (?, ?, ?)", (pseudo, ip, 0))
        conn.commit()

def create_match(pseudo1, pseudo2, ip1, ip2):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO matchs (joueur1_ip, joueur2_ip, joueur1_pseudo, joueur2_pseudo) VALUES (?, ?, ?, ?)",
            (ip1, ip2, pseudo1, pseudo2)
        )
        match_id = cursor.lastrowid
        conn.commit()
        return match_id

def insert_tour(match_id, joueur, coup):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tours (id_match, joueur, coup) VALUES (?, ?, ?)", (match_id, joueur, coup))
        conn.commit()

def update_match_result(match_id, plateau, gagnant):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE matchs SET plateau = ?, fini = 1, resultat = ? WHERE id = ?", (plateau, gagnant, match_id))
        conn.commit()

# === Matchmaking ===
@socketio.on('join')
def handle_join(data):
    pseudo = data.get("pseudo")
    sid = request.sid
    ip = request.remote_addr

    sid_to_pseudo[sid] = pseudo
    sid_to_ip[sid] = ip

    # 🧹 Nettoie ancien choix
    if sid in choices:
        del choices[sid]

    insert_in_file(pseudo, ip)

    waiting_players.append(sid)
    print(f"👤 {pseudo} rejoint la file ({ip})")

    if len(waiting_players) >= 2:
        p1, p2 = waiting_players.pop(0), waiting_players.pop(0)
        threading.Thread(target=start_match, args=(p1, p2)).start()


# === Jeu ===
choices = {}  # {sid: "pierre"}

def start_match(p1, p2):
    print(">> Start match entre", p1, "et", p2)
    print(">> sid_to_pseudo :", sid_to_pseudo)
    print(">> sid_to_ip :", sid_to_ip)

    pseudo1 = sid_to_pseudo.get(p1)
    pseudo2 = sid_to_pseudo.get(p2)

    if not pseudo1 or not pseudo2:
        print("⚠️ Impossible de trouver les pseudos des joueurs.")
        return

    ip1 = sid_to_ip.get(p1)
    ip2 = sid_to_ip.get(p2)

    print(f"🎮 Match entre {pseudo1} ({ip1}) et {pseudo2} ({ip2})")

    match_id = create_match(pseudo1, pseudo2, ip1, ip2)
    socketio.emit("start_match", {"opponent": pseudo2}, to=p1)
    socketio.emit("start_match", {"opponent": pseudo1}, to=p2)

    def receive_choices():
        while True:
            if p1 in choices and p2 in choices:
                c1, c2 = choices[p1], choices[p2]
                insert_tour(match_id, pseudo1, c1)
                insert_tour(match_id, pseudo2, c2)
                gagnant = compute_winner(c1, c2)
                update_match_result(match_id, f"{c1}-{c2}", gagnant)
                socketio.emit("match_result", {
                    "your_choice": c1,
                    "opponent_choice": c2,
                    "result": get_result_label("joueur1", gagnant)
                }, to=p1)
                socketio.emit("match_result", {
                    "your_choice": c2,
                    "opponent_choice": c1,
                    "result": get_result_label("joueur2", gagnant)
                }, to=p2)
                del choices[p1]
                del choices[p2]
                break

    threading.Thread(target=receive_choices).start()

@socketio.on("player_choice")
def on_choice(data):
    sid = request.sid
    choice = data.get("choice")
    choices[sid] = choice

# === Logique PPC ===
def compute_winner(c1, c2):
    rules = {
        "pierre": "ciseaux",
        "ciseaux": "papier",
        "papier": "pierre"
    }
    if c1 == c2:
        return "egalite"
    elif rules[c1] == c2:
        return "joueur1"
    else:
        return "joueur2"

def get_result_label(joueur, gagnant):
    if gagnant == "egalite":
        return "égalité"
    return "gagné" if joueur == gagnant else "perdu"

# === Classement accessible aux joueurs ===
@app.route('/classement')
def public_classement():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT t.joueur, COUNT(*) as victoires
        FROM tours t
        JOIN matchs m ON t.id_match = m.id
        WHERE 
            (m.resultat = 'joueur1' AND t.joueur = m.joueur1_pseudo)
            OR 
            (m.resultat = 'joueur2' AND t.joueur = m.joueur2_pseudo)
        GROUP BY t.joueur
        ORDER BY victoires DESC
        """)
        classement = cursor.fetchall()
    return render_template("classement.html", classement=classement)

# === Interface Web Utilisateur ===
@app.route('/')
def index():
    return render_template("index.html")

# === Authentification Admin ===
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'Mahdi' and password == 'admin123':
            session['admin_logged_in'] = True
            session['admin_user'] = username
            return redirect(url_for('admin_panel'))
        else:
            return render_template('login.html', error="Nom d'utilisateur ou mot de passe incorrect")
    return render_template('login.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('index'))

# === Interface Admin (CRUD) ===
@app.route('/admin')
def admin_panel():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM file_attente")
        file_attente = cursor.fetchall()
    return render_template("admin.html", file_attente=file_attente, admin_user=session.get("admin_user"))

@app.route('/admin/file_attente/new', methods=["GET", "POST"])
def new_file_attente():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    if request.method == "POST":
        pseudo = request.form["pseudo"]
        ip = request.form["ip"]
        port = request.form["port"]
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO file_attente (pseudo, ip, port) VALUES (?, ?, ?)", (pseudo, ip, port))
            conn.commit()
        return redirect(url_for("admin_panel"))
    return render_template("new_file_attente.html")

@app.route('/admin/file_attente/edit/<int:id>', methods=["GET", "POST"])
def edit_file_attente(id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        if request.method == "POST":
            pseudo = request.form["pseudo"]
            ip = request.form["ip"]
            port = request.form["port"]
            cursor.execute("UPDATE file_attente SET pseudo = ?, ip = ?, port = ? WHERE id = ?", (pseudo, ip, port, id))
            conn.commit()
            return redirect(url_for("admin_panel"))
        cursor.execute("SELECT * FROM file_attente WHERE id = ?", (id,))
        joueur = cursor.fetchone()
    return render_template("edit_file_attente.html", joueur=joueur)

@app.route('/admin/file_attente/delete/<int:id>')
def delete_file_attente(id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM file_attente WHERE id = ?", (id,))
        conn.commit()
    return redirect(url_for("admin_panel"))

# === Lancement Serveur ===
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
