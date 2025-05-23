# 🎮 ProjetDev

ProjetDev est une application web développée en Python avec le micro-framework Flask.  
Ce projet a été réalisé dans un cadre pédagogique afin de mettre en pratique les bases du développement web en Python, la gestion de bases de données SQLite, et l’architecture MVC avec Flask.

---

## 🔍 Fonctionnalités principales

- 🖥️ Interface web dynamique avec Flask et Jinja2
- 🗃️ Base de données SQLite (`matchmaking.db`)
- 📄 Templates HTML pour la partie frontend (`templates/`)
- 🎨 Intégration CSS/JS via le dossier `static/`
- ⚙️ Script d’initialisation de la base de données (`init_db.py`)
- 🚀 Démarrage rapide avec `server.py`

---

## 🏗️ Structure du projet

```
ProjetDev/
├── init_db.py            # Script de création/init de la base SQLite
├── matchmaking.db        # Base de données SQLite
├── server.py             # Serveur principal Flask
├── static/               # Fichiers statiques (CSS, JS)
│   ├── css/
│   └── js/
├── templates/            # Fichiers HTML avec Jinja2
│   └── ...
└── README.md             # Ce fichier
```

---

## ⚙️ Installation & Lancement

### 1. Cloner le projet

```bash
git clone https://github.com/FMatteoYnov/ProjetDev.git
cd ProjetDev
```

### 2. Créer un environnement virtuel (recommandé)

```bash
python -m venv venv
# Linux/macOS :
source venv/bin/activate
# Windows :
venv\Scripts\activate
```

### 3. Installer Flask

```bash
pip install flask
```

### 4. Initialiser la base de données

```bash
python init_db.py
```

### 5. Lancer le serveur

```bash
python server.py
```

### 6. Accéder à l'application

Ouvrir votre navigateur à l’adresse suivante :  
👉 [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🧪 Technologies utilisées

- **Python 3**
- **Flask**
- **SQLite**
- **HTML/CSS/JS**
- **Jinja2**

---

## 📌 À propos

Ce projet a été réalisé dans le cadre d’un module de développement logiciel. Il a pour objectif de démontrer la création d’un site web simple, avec gestion de données côté serveur et affichage côté client via templates HTML.

---

## 🤝 Contribuer

Les contributions sont les bienvenues !  
N’hésitez pas à :

- Fork le projet
- Créer une nouvelle branche
- Proposer une Pull Request

---

## 👤 Auteur

**FMatteoYnov**  
🔗 [GitHub](https://github.com/FMatteoYnov)

---

## 📝 Licence

Ce projet est open-source — vous pouvez l’utiliser à des fins pédagogiques ou personnelles.
