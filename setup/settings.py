# settings.py - ATUALIZADO COM ANALYTICS

"""
Django settings for setup project - COM ANALYTICS GEOGRÁFICO
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-4b+u1%+l-59=b+074f^46gc@f=))xh7e_zwkpwd0v4#=nu5s2a'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']  # Em produção, especifique os domínios permitidos

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Apps do projeto
    'home',
    'ThreePhaseCoils',
    'ThreePhasePower',
    'ThreePhaseDiagram',
    
    # NOVO APP DE ANALYTICS
    'analytics',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # MIDDLEWARE DE ANALYTICS - Adicionar APÓS SessionMiddleware e AuthenticationMiddleware
    'analytics.middleware.GeoLocationMiddleware',
    'analytics.middleware.CalculationTrackingMiddleware',
]

ROOT_URLCONF = 'setup.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
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

WSGI_APPLICATION = 'setup.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Cache Configuration (para armazenar dados de geolocalização)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Content Security Policy (CSP)
CSP_SCRIPT_SRC = (
    "'self'",
    "'unsafe-inline'",
    "https://code.jquery.com",
    "https://cdn.jsdelivr.net",
    "https://unpkg.com",  # Para Leaflet
    "https://cdn.jsdelivr.net/npm/chart.js",  # Para Chart.js
)

CSP_STYLE_SRC = (
    "'self'",
    "'unsafe-inline'",
    "https://cdn.jsdelivr.net",
    "https://unpkg.com",  # Para Leaflet CSS
)

CSP_IMG_SRC = (
    "'self'",
    "data:",
    "https:",
    "http://",  # Para tiles do OpenStreetMap
)

CSP_CONNECT_SRC = (
    "'self'",
    "https://ipapi.co",  # API de geolocalização
    "http://ip-api.com",  # API de geolocalização fallback
    "https://*.tile.openstreetmap.org",  # Tiles do mapa
)

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'analytics.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'analytics': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Analytics Settings (configurações específicas do sistema de analytics)
ANALYTICS_CONFIG = {
    'ENABLE_TRACKING': True,  # Habilita/desabilita rastreamento
    'TRACK_BOTS': False,  # Se deve rastrear bots/crawlers
    'GEOLOCATION_CACHE_HOURS': 24,  # Tempo de cache para dados de geolocalização
    'MAX_REQUESTS_PER_DAY': 1000,  # Limite de requisições para API de geolocalização
}