<br>

# Wichtige PY Django Commands

<br>

# Venv Einrichten

#### Venv erstellen

```bash
python -m venv .venv
```

#### Unter Windows

```bash
.venv\Scripts\activate
```

#### Unter macOS und Linux

```bash
source .venv/bin/activate
```

oder

```bash
. .venv/bin/activate
. .venv/bin/activate.bash
. .venv/bin/activate.fish
```

<br>

# Installation / Ersteinrichtung

#### Installiert das Framework Django

```bash
python -m pip install Django
```

#### Ein neues Django Backend Api Projekt anlegen

```bash
django-admin startproject core .
```

<br>

#### Installiert das Rest Framework

```bash
pip install djangorestframework
```

#### Erstellt eine neue App

```bash
python manage.py startapp app_name
```

Was nicht fehlen darf bei jeder app. Der Grundaufbau:

```
app_name/
├── models.py
├── admin.py
├── apps.py
├── tests/
│   ├── __init__.py
│   └── test.py
└── api/
    ├── __init__.py
    ├── views.py
    ├── utils.py
    ├── serializers.py
    ├── urls.py
    └── permissions.py
```

*Wichtig*: `__init__.py` muss im `api/` Ordner vorhanden sein, damit Python den Ordner als Modul erkennt.

*Wichtig*: das rest_framework sowie weitere apps müssen in der settings.py installiert werden

```
< SETTINGS.PY >

INSTALLED_APPS = [
  "rest_framework",
  "app_name",
]
```

Zusatz info:

```
< SETTINGS.PY >

MIDDLEWARE = [
    Dieser Eintrag eventuell => 'django.middleware.csrf.CsrfViewMiddleware',
    Auskommentieren => # 'django.middleware.csrf.CsrfViewMiddleware',
]

CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:5500',
    'http://localhost:5500',
]
CORS_ALLOWED_ORIGINS = [
    'http://127.0.0.1:5500',
    'http://localhost:5500',
]

=============================================================================

< URLS.PY >

urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
]
```

<br>

# .env & Secrets

#### Installiert python-dotenv

```bash
pip install python-dotenv
```

#### .env Datei anlegen (im Root-Verzeichnis, neben manage.py)

```
.env
```

#### Inhalt der .env Datei

```
# Django
SECRET_KEY=dein-geheimer-schluessel-hier
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Datenbank (Beispiel für PostgreSQL)
DATABASE_URL=postgres://user:password@localhost:5432/dbname

# CORS / CSRF
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:5500,http://localhost:5500
CORS_ALLOWED_ORIGINS=http://127.0.0.1:5500,http://localhost:5500
```

#### .env in settings.py einlesen

```python
< SETTINGS.PY >

import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
```

*Wichtig*: Die `.env` Datei niemals in Git committen! Siehe `.gitignore` Abschnitt.

<br>

# Git & .gitignore

#### Git Repository initialisieren

```bash
git init
```

#### .gitignore Datei anlegen

```bash
touch .gitignore
```

#### Inhalt der .gitignore

```
# Virtual Environment
.venv/
venv/
env/

# Secrets
.env
.env.*
!.env.example

# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
*.pyc

# Django
db.sqlite3
db.sqlite3-journal
*.log
media/
staticfiles/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
```

*Tipp*: Eine `.env.example` Datei mit leeren Werten anlegen und in Git committen, damit andere Entwickler wissen, welche
Variablen benötigt werden.

```
# .env.example
SECRET_KEY=
DEBUG=
ALLOWED_HOSTS=
DATABASE_URL=
```

<br>

# CORS

#### Installiert django-cors-headers

```bash
pip install django-cors-headers
```

#### In settings.py einrichten

```
< SETTINGS.PY >

INSTALLED_APPS = [
    "corsheaders",
    ...
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",   # Muss vor CommonMiddleware stehen!
    "django.middleware.common.CommonMiddleware",
    ...
]

CORS_ALLOWED_ORIGINS = [
    'http://127.0.0.1:5500',
    'http://localhost:5500',
]
```

<br>

# Statische Dateien

#### In settings.py konfigurieren

```
< SETTINGS.PY >

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

#### Statische Dateien sammeln (für Produktion)

```bash
python manage.py collectstatic
```

<br>

# Requirements

#### Requirements Datei erstellen

```bash
pip freeze > requirements.txt
```

#### Requirements installieren (z.B. nach git clone)

```bash
pip install -r requirements.txt
```

<br>

# DB

#### Erstellt Migrationsdateien von Änderungen an Models

```bash
python manage.py makemigrations
```

#### Übernimmt die Änderungen in die Datenbank

```bash
python manage.py migrate
```

<br>

# Admin Erstellen

#### Erstellt einen Admin User

```bash
python manage.py createsuperuser
```

<br>

# Authentifizierung

## Basic Auth

Ist in Django REST Framework bereits eingebaut — kein extra Package nötig.
Credentials werden als Base64-kodierter String im Header mitgeschickt.
*Nur über HTTPS verwenden!*

```
< SETTINGS.PY >

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

```python
< VIEWS.PY >

from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

class MeineView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"user": request.user.username})
```

<br>

## Token Auth

Einfaches Token-System — ein Token pro User, serverseitig gespeichert.

```bash
pip install djangorestframework
```

```
< SETTINGS.PY >

INSTALLED_APPS = [
    "rest_framework",
    "rest_framework.authtoken",   # Token App hinzufügen
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

```bash
python manage.py migrate
```

Token-Endpoint in urls.py einbinden:

```python
< URLS.PY >

from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('api/token/', obtain_auth_token),   # POST: username + password → token
]
```

Token manuell für einen User erstellen:

```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> from rest_framework.authtoken.models import Token
>>> user = User.objects.get(username='admin')
>>> token, created = Token.objects.get_or_create(user=user)
>>> print(token.key)
```

Request mit Token:

```
Authorization: Token <dein-token>
```

<br>

## JWT Auth (empfohlen für APIs)

Stateless — kein Datenbank-Lookup pro Request nötig.
Access Token (kurzlebig) + Refresh Token (langlebig).

```bash
pip install djangorestframework-simplejwt
```

```
< SETTINGS.PY >

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}
```

```python
< URLS.PY >

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view()),         # POST: login → access + refresh
    path('api/token/refresh/', TokenRefreshView.as_view()),    # POST: refresh → neuer access token
]
```

Request mit JWT:

```
Authorization: Bearer <access-token>
```

Aufbau des Token-Flows:

```
1. POST /api/token/         { username, password }  →  { access, refresh }
2. Request mit access token im Header
3. Access token abgelaufen → POST /api/token/refresh/  { refresh }  →  { access }
```

<br>

## OAuth2 (Social Login / Third-Party)

Für Login mit Google, GitHub, etc. oder komplexe Drittanbieter-Flows.

```bash
pip install django-allauth
```

```
< SETTINGS.PY >

INSTALLED_APPS = [
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',   # Beispiel: Google
    'allauth.socialaccount.providers.github',   # Beispiel: GitHub
]

MIDDLEWARE = [
    ...
    'allauth.account.middleware.AccountMiddleware',
]

SITE_ID = 1
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}
```

```python
< URLS.PY >

urlpatterns = [
    path('accounts/', include('allauth.urls')),
]
```

```bash
python manage.py migrate
```

*Wichtig*: Client ID + Secret vom jeweiligen Provider (Google Cloud Console, GitHub Settings)
in der Django Admin unter *Social Applications* eintragen.

Vergleich der Auth-Methoden:

```
Basic Auth    →  Einfach, nur HTTPS, kein Logout möglich
Token Auth    →  Einfach, Token widerrufbar, DB-Lookup pro Request
JWT           →  Stateless, skalierbar, empfohlen für SPAs / Mobile
OAuth2        →  Social Login, Third-Party, komplex aber mächtig
```

<br>

# Dev

#### Startet einen Dev Server

```bash
python manage.py runserver
```

#### Führt Django eigene API Tests aus

```bash
python manage.py test
```