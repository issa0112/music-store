import environ
import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# =========================
# CHARGEMENT DU .env
# =========================
load_dotenv()

# =========================
# BASE DIR
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# ENVIRONNEMENT
# =========================
DEBUG = os.getenv("DJANGO_ENV") != "production"
SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-dev-key")

ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1,tramo.com,www.tramo.com,music-store-ngen.onrender.com"
).split(",")

# =========================
# APPLICATIONS
# =========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',

    'storages',

    'store',
    'Utilisateurs',
    "django_celery_results",
    "django_celery_beat",
]

SITE_ID = 1

# =========================
# MIDDLEWARE
# =========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'allauth.account.middleware.AccountMiddleware',
]

# =========================
# URLS / TEMPLATES
# =========================
ROOT_URLCONF = 'music_store.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'music_store.wsgi.application'

# =========================
# DATABASES
# =========================
if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': dj_database_url.parse(
            os.getenv("DATABASE_URL"),
            conn_max_age=600,
            ssl_require=True
        )
    }

# =========================
# PASSWORDS
# =========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =========================
# I18N
# =========================
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# =========================
# STATIC FILES
# =========================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATICFILES_DIRS = [
    BASE_DIR / 'store' / 'static',
]

# =========================
# MEDIA FILES → BACKBLAZE B2
# =========================

# Variables AWS
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")  # bucket privé

AWS_ACCESS_KEY_ID_IMAGES = os.getenv("AWS_ACCESS_KEY_ID_IMAGES")
AWS_SECRET_ACCESS_KEY_IMAGES = os.getenv("AWS_SECRET_ACCESS_KEY_IMAGES")
AWS_STORAGE_BUCKET_NAME_IMAGES = os.getenv("AWS_STORAGE_BUCKET_NAME_IMAGES")  # bucket public

AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")

AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = False
AWS_S3_ADDRESSING_STYLE = "virtual"

# Configuration stockage
if DEBUG:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    MEDIA_ROOT = BASE_DIR / "media"
    MEDIA_URL = "/media/"
else:
    DEFAULT_FILE_STORAGE = 'store.storage_backends.MediaStorage'
    MEDIA_URL = f"https://f000.backblazeb2.com/file/{AWS_STORAGE_BUCKET_NAME}/"


# =========================
# AUTH / ALLAUTH
# =========================
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True

# =========================
# STRIPE
# =========================
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")

# =========================
# SECURE HTTPS (Render)
# =========================
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# =========================
# LOGGING
# =========================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# =========================
# DEFAULT PK
# =========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_BACKEND = "django-db"

CELERY_CACHE_BACKEND = "django-cache" # Scheduler pour Celery Beat (stockage en base via django_celery_beat) 
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"