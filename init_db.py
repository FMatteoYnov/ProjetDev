import sqlite3

conn = sqlite3.connect("matchmaking.db")
cursor = conn.cursor()

# === Table file d'attente ===
cursor.execute("""
CREATE TABLE IF NOT EXISTS file_attente (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pseudo TEXT NOT NULL,
    ip TEXT NOT NULL,
    port INTEGER,
    date_entree DATETIME DEFAULT CURRENT_TIMESTAMP
);
""")

# === Table des matchs (créée sans les nouvelles colonnes si déjà existante) ===
cursor.execute("""
CREATE TABLE IF NOT EXISTS matchs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    joueur1_ip TEXT NOT NULL,
    joueur2_ip TEXT NOT NULL,
    plateau TEXT,
    fini BOOLEAN DEFAULT 0,
    resultat TEXT
);
""")

# === Ajout conditionnel des colonnes joueur1_pseudo et joueur2_pseudo ===
existing_columns = [col[1] for col in cursor.execute("PRAGMA table_info(matchs)").fetchall()]

if "joueur1_pseudo" not in existing_columns:
    cursor.execute("ALTER TABLE matchs ADD COLUMN joueur1_pseudo TEXT;")
    print("✅ Colonne 'joueur1_pseudo' ajoutée.")

if "joueur2_pseudo" not in existing_columns:
    cursor.execute("ALTER TABLE matchs ADD COLUMN joueur2_pseudo TEXT;")
    print("✅ Colonne 'joueur2_pseudo' ajoutée.")

# === Table des tours ===
cursor.execute("""
CREATE TABLE IF NOT EXISTS tours (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_match INTEGER NOT NULL,
    joueur TEXT NOT NULL,
    coup TEXT NOT NULL,
    FOREIGN KEY(id_match) REFERENCES matchs(id)
);
""")

conn.commit()
conn.close()

print("✅ Base de données vérifiée et mise à jour avec les colonnes de pseudos.")
