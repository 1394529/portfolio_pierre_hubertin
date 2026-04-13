# Pierre Hubertin — Portfolio Django

> Site portfolio professionnel Data Analyst — Power BI | SQL | BI Reporting  
> Stack : Python 3.11+ / Django 5 / WhiteNoise / SQLite → PostgreSQL (prod)

---

## 📋 Table des matières

1. [Aperçu de l'architecture](#architecture)
2. [Installation locale](#installation)
3. [Configuration des variables d'environnement](#configuration)
4. [Chargement des données initiales](#fixtures)
5. [Personnalisation du contenu](#personnalisation)
6. [Lancer les tests](#tests)
7. [Déploiement en production](#deploiement)
8. [Structure du projet](#structure)

---

## Architecture <a name="architecture"></a>

```
portfolio/
├── portfolio_project/          # Configuration Django
│   ├── settings.py             # Paramètres (env vars via python-decouple)
│   ├── urls.py                 # Routage racine + handlers d'erreur
│   ├── wsgi.py / asgi.py
│
├── core/                       # Application principale
│   ├── models.py               # Project, Skill, BlogPost, ContactMessage
│   ├── views.py                # index, project_detail, blog, contact AJAX
│   ├── forms.py                # ContactForm (honeypot + validation serveur)
│   ├── urls.py                 # Routes de l'app (namespace: core)
│   ├── admin.py                # Interface d'administration
│   ├── context_processors.py   # Variables globales (nom, liens, etc.)
│   ├── tests.py                # Tests unitaires + intégration (45+ tests)
│   ├── fixtures/
│   │   └── initial_data.json   # Données de démonstration
│   └── templatetags/
│       └── portfolio_tags.py   # Filtre |split
│
├── static/
│   ├── css/main.css            # Design system complet (CSS variables)
│   ├── js/main.js              # Navbar, scroll, skill bars, form AJAX
│   └── cv/                     # → Déposer pierre_hubertin_cv.pdf ici
│
├── templates/
│   ├── base.html               # Layout principal (navbar + footer)
│   ├── index.html              # Page unique (Hero, Projets, Skills, Blog, Contact)
│   ├── core/
│   │   ├── project_detail.html
│   │   ├── blog_list.html
│   │   └── blog_detail.html
│   └── errors/
│       ├── 404.html
│       └── 500.html
│
├── .env.example                # Template de configuration
├── requirements.txt
├── pytest.ini
├── Procfile                    # Heroku / Railway
└── manage.py
```

---

## Installation locale <a name="installation"></a>

### Prérequis
- Python 3.11+
- pip / virtualenv

### Étapes

```bash
# 1. Cloner le dépôt
git clone https://github.com/pierre-hubertin/portfolio.git
cd portfolio

# 2. Créer et activer l'environnement virtuel
python -m venv venv
source venv/bin/activate          # Linux/Mac
# venv\Scripts\activate           # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos valeurs (voir section Configuration)

# 5. Appliquer les migrations
python manage.py migrate

# 6. Charger les données de démonstration
python manage.py loaddata core/fixtures/initial_data.json

# 7. Créer un super-utilisateur admin
python manage.py createsuperuser

# 8. Démarrer le serveur de développement
python manage.py runserver
```

Accéder à : http://127.0.0.1:8000  
Interface admin : http://127.0.0.1:8000/admin/

---

## Configuration des variables d'environnement <a name="configuration"></a>

Copier `.env.example` vers `.env` et remplir :

| Variable | Défaut | Description |
|---|---|---|
| `SECRET_KEY` | *(insecure)* | Clé secrète Django — **obligatoire en prod** |
| `DEBUG` | `True` | `False` en production |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Domaines autorisés |
| `DB_NAME` | `db.sqlite3` | Nom du fichier SQLite |
| `EMAIL_BACKEND` | `console.EmailBackend` | Backend courriel |
| `EMAIL_HOST_USER` | *(vide)* | Adresse Gmail / SMTP |
| `EMAIL_HOST_PASSWORD` | *(vide)* | Mot de passe app Gmail |
| `CONTACT_EMAIL` | *(vide)* | Destinataire des messages de contact |

---

## Chargement des données initiales <a name="fixtures"></a>

Les fixtures `core/fixtures/initial_data.json` contiennent :
- 4 catégories de compétences avec 12 compétences
- 3 projets de démonstration
- 3 articles de blog

```bash
python manage.py loaddata core/fixtures/initial_data.json
```

Pour réinitialiser complètement :
```bash
python manage.py flush --no-input
python manage.py loaddata core/fixtures/initial_data.json
```

---

## Personnalisation du contenu <a name="personnalisation"></a>

### 1. Identité (immédiat)
Modifier `core/context_processors.py` :
```python
'OWNER_NAME':     'Votre Nom',
'OWNER_EMAIL':    'votre@email.com',
'OWNER_GITHUB':   'https://github.com/votre-profil',
'OWNER_LINKEDIN': 'https://linkedin.com/in/votre-profil',
'OWNER_LOCATION': 'Votre ville, Province',
```

### 2. CV PDF
Déposer votre CV dans `static/cv/pierre_hubertin_cv.pdf`  
*(ou modifier `CV_DOWNLOAD_URL` dans `context_processors.py`)*

### 3. Projets, compétences, articles
Gérer via l'interface Django Admin : `/admin/`  
- **Projets** → Ajouter avec miniature, liens GitHub/live, technologies
- **Compétences** → Organiser par catégories, ajuster niveaux et %
- **Articles** → Rédiger en HTML, définir le statut Publié/Brouillon

### 4. Palette de couleurs
Modifier les variables CSS dans `static/css/main.css` :
```css
:root {
  --neon:     #00FF88;  /* Couleur d'accent principale */
  --obsidian: #0A0F0D;  /* Fond principal */
  --carbon:   #111816;  /* Fond secondaire */
  --slate:    #6B7F74;  /* Texte de support */
}
```

### 5. Miniatures de projets
- Format recommandé : 800×450px (ratio 16:9), JPEG/WebP
- Déposer dans `media/projects/thumbnails/` ou via l'admin

---

## Lancer les tests <a name="tests"></a>

```bash
# Tous les tests avec pytest
pytest

# Avec rapport de couverture
coverage run -m pytest
coverage report

# Tests Django standard
python manage.py test core

# Test spécifique
pytest core/tests.py::ContactFormTest -v
pytest core/tests.py::ContactAjaxViewTest::test_valid_submission_saves_to_db -v
```

**Couverture des tests (45+ cas) :**
- ✅ Modèles : slugs auto, `get_technologies_list`, `get_stars`, `is_published`
- ✅ Formulaire : validation, honeypot anti-spam, messages d'erreur FR
- ✅ Vues : codes HTTP, templates utilisés, contenu du contexte
- ✅ Contact AJAX : soumission valide/invalide, sauvegarde DB
- ✅ Routage URL : résolution de toutes les routes
- ✅ Context processors : variables globales disponibles dans les templates

---

## Déploiement en production <a name="deploiement"></a>

### Option A — Railway / Render (recommandé, gratuit)

1. Pousser le code sur GitHub
2. Créer un nouveau projet Railway depuis GitHub
3. Ajouter les variables d'environnement dans Railway Dashboard :
   ```
   SECRET_KEY=<générer une clé sécurisée>
   DEBUG=False
   ALLOWED_HOSTS=votre-domaine.up.railway.app
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST_USER=...
   EMAIL_HOST_PASSWORD=...
   CONTACT_EMAIL=...
   ```
4. Railway détecte automatiquement le `Procfile`

### Option B — VPS (Ubuntu + Nginx + Gunicorn)

```bash
# Sur le serveur
git clone ... && cd portfolio
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env && nano .env  # remplir les valeurs prod

python manage.py migrate
python manage.py loaddata core/fixtures/initial_data.json
python manage.py createsuperuser
python manage.py collectstatic --no-input

# Gunicorn
gunicorn portfolio_project.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

Configuration Nginx (exemple) :
```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location /static/ { alias /path/to/portfolio/staticfiles/; }
    location /media/  { alias /path/to/portfolio/media/; }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Checklist production
- [ ] `DEBUG=False` dans `.env`
- [ ] `SECRET_KEY` aléatoire et longue (50+ caractères)
- [ ] `ALLOWED_HOSTS` contient votre domaine réel
- [ ] `python manage.py collectstatic` exécuté
- [ ] Certificat SSL/HTTPS configuré (Let's Encrypt via Certbot)
- [ ] Backup de la base de données planifié
- [ ] CV PDF déposé dans `static/cv/`

---

## Générer une SECRET_KEY sécurisée

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

*Développé avec Django 5 · Python 3.11 · CSS personnalisé · Esthétique terminal néon*
