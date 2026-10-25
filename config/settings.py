"""
Django settings for JobTrack project.
"""

import os
from pathlib import Path
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-u828&lp(#cz(b!f0y!f(pl(mtiipumqyo-1dn%5uy7aahk&mpf'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

# Render & Host Configurations
HEALTHCHECK_APPLICATION_URL = os.environ.get('HEALTHCHECK_APPLICATION_URL', '').strip().rstrip('/')
HEALTHCHECK_ADMIN_USERNAME = os.environ.get('HEALTHCHECK_ADMIN_USERNAME', 'kanishkan').strip()
HEALTHCHECK_TIME_ZONE = os.environ.get('HEALTHCHECK_TIME_ZONE', os.environ.get('TIME_ZONE', 'UTC')).strip()
PYTHON_VERSION = os.environ.get('PYTHON_VERSION', '3.14.0').strip()

# Key Vault Users Configuration (strictly pulled from environment)
USER_1_USERNAME = os.environ.get('USER_1_USERNAME', 'kanishkan').strip()
USER_1_PASSWORD = os.environ.get('USER_1_PASSWORD', 'Kanishkan@2004')
USER_2_USERNAME = os.environ.get('USER_2_USERNAME', 'preetha').strip()
USER_2_PASSWORD = os.environ.get('USER_2_PASSWORD', 'Preetha@2005')
RENDER_USERS = os.environ.get('RENDER_USERS', '').strip()


# Render Environment & Host Detection
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '').strip()
if RENDER_EXTERNAL_HOSTNAME and not HEALTHCHECK_APPLICATION_URL:
    HEALTHCHECK_APPLICATION_URL = f"https://{RENDER_EXTERNAL_HOSTNAME}"

# ALLOWED_HOSTS Configuration
# Render health checks ping internal private IPs (10.x.x.x) and Go-http-client on 127.0.0.1.
# On Render (RENDER=true), allow wildcard '*' so internal health checks return 200 OK without DisallowedHost 400.
raw_hosts = os.environ.get('ALLOWED_HOSTS', '*').split(',')
ALLOWED_HOSTS = [h.strip() for h in raw_hosts if h.strip()]

if os.environ.get('RENDER') or '*' in ALLOWED_HOSTS or not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ['*']
else:
    for host in ['localhost', '127.0.0.1', '[::1]', '.onrender.com']:
        if host not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(host)

# CSRF Trusted Origins
raw_origins = os.environ.get('CSRF_TRUSTED_ORIGINS', 'http://127.0.0.1,http://localhost').split(',')
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in raw_origins if origin.strip()]

if RENDER_EXTERNAL_HOSTNAME:
    ext_origin = f"https://{RENDER_EXTERNAL_HOSTNAME}"
    if ext_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(ext_origin)

if HEALTHCHECK_APPLICATION_URL and HEALTHCHECK_APPLICATION_URL not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append(HEALTHCHECK_APPLICATION_URL)

# Wildcard for all Render subdomains to prevent any CSRF issues
if 'https://*.onrender.com' not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append('https://*.onrender.com')


# Redis Cache Integration
REDIS_URL = os.environ.get('REDIS_URL', '').strip()
if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }

# Supabase Storage & Services Integration
SUPABASE_URL = os.environ.get('SUPABASE_URL', '').strip().rstrip('/')
SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '').strip()
SUPABASE_STORAGE_BUCKET = os.environ.get('SUPABASE_STORAGE_BUCKET', 'resumes').strip()


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Local apps
    'tracker.apps.TrackerConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'tracker.middleware.AbsoluteSessionTimeoutMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# Default to SQLite, override with DATABASE_URL (e.g. Postgres on Render/Railway)
default_db_url = f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
database_url = os.environ.get('DATABASE_URL', default_db_url)

DATABASES = {
    'default': dj_database_url.config(
        default=database_url,
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 6},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = HEALTHCHECK_TIME_ZONE
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
] if (BASE_DIR / 'static').exists() else []
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Authentication URLs
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'
SESSION_COOKIE_AGE = 20 * 60
SESSION_SAVE_EVERY_REQUEST = False

# Email backend (console by default for dev, easily configured via env)
EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend'
)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
