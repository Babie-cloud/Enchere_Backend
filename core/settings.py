"""
Django settings for core project.
"""

from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-m_ciku%59ulq@+-r602n6$e5iw#(=+8@0d0++qp3l6pun5yje2'

DEBUG = True

ALLOWED_HOSTS = ['*']               # ← ajouté pour dev (localhost, 127.0.0.1, etc.)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    # 'parler',
    # 'parler_rest',
    'djoser',

    # Nos applications
    'users.apps.UsersConfig',
    'produits.apps.ProduitsConfig',
    'commandes.apps.CommandesConfig',
    'factures.apps.FacturesConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',          # doit rester en haut
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.debug',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

STATIC_URL = 'static/'

AUTH_USER_MODEL = 'users.Utilisateur'

# ==================== REST FRAMEWORK CONFIG ====================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',   # ← utile pour debug dans navigateur
    ),
}

# En DEBUG → on assouplit les permissions globales (mais pas sur les vues sensibles)
if DEBUG:
    REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = [
        'rest_framework.permissions.AllowAny',
    ]

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,           # ← bonne pratique
}

# CORS – configuration plus permissive pour le dev (à restreindre en prod !)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]

CORS_ALLOW_CREDENTIALS = True                       # ← important si tu utilises cookies/session
CORS_ALLOW_HEADERS = [                              # ← autorise le header Authorization
    "accept",
    "authorization",
    "content-type",
    "x-csrftoken",
    "x-requested-with",
]

# ==================== EMAIL CONFIG ====================
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.mailtrap.io'
# EMAIL_PORT = 2525
# EMAIL_HOST_USER = 'ton_vrai_username_mailtrap'
# EMAIL_HOST_PASSWORD = 'ton_vrai_password_mailtrap'
# EMAIL_USE_TLS = True
# DEFAULT_FROM_EMAIL = 'DirectAlu <no-reply@directalu.com>'

# ==================== DJOSER CONFIG ====================
DJOSER = {
    'LOGIN_FIELD': 'email',
    'USER_CREATE_PASSWORD_RETYPE': True,
    'USERNAME_CHANGED_EMAIL_CONFIRMATION': True,
    'PASSWORD_CHANGED_EMAIL_CONFIRMATION': True,
    'SEND_CONFIRMATION_EMAIL': False,
    'SET_PASSWORD_RETYPE': True,
    'SET_USERNAME_RETYPE': True,
    'PASSWORD_RESET_CONFIRM_URL': 'password/reset/confirm/{uid}/{token}',
    'USERNAME_RESET_CONFIRM_URL': 'email/reset/confirm/{uid}/{token}',
    'ACTIVATION_URL': 'activate/{uid}/{token}',
    'SEND_ACTIVATION_EMAIL': False,
    'SERIALIZERS': {
        'user_create': 'users.api.serializers.RegisterSerializer',
        'user': 'users.api.serializers.UserSerializer',
        'current_user': 'users.api.serializers.UserSerializer',
        'token_create': 'users.api.serializers.CustomTokenObtainPairSerializer',
    },
}

# ==================== REDIRECTIONS & AUTH ====================
LOGIN_REDIRECT_URL = '/api/produits/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/api-auth/login/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'