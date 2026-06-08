"""
Django settings for FAQ Crowdsourcing Platform.
"""
from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-only-change-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

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
    'allauth.socialaccount.providers.google',
    'taggit',
    'crispy_forms',
    'crispy_bootstrap5',
    'accounts',
    'faqs',
    'qa',
    'community',
    'moderation',
    'analytics',
    'assistant',
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
    'allauth.account.middleware.AccountMiddleware',
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
                'community.context_processors.notification_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASE_URL = config('DATABASE_URL', default='')
if DATABASE_URL.startswith('postgres'):
    import re
    match = re.match(
        r'postgres(?:ql)?://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)',
        DATABASE_URL,
    )
    if match:
        user, password, host, port, name = match.groups()
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': name,
                'USER': user,
                'PASSWORD': password,
                'HOST': host,
                'PORT': port,
                'CONN_MAX_AGE': 60,
            }
        }
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
else:
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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'faqs:home'
LOGOUT_REDIRECT_URL = 'faqs:home'

EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@faqplatform.local')

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# Reputation points
POINTS_ANSWER_POSTED = config('POINTS_ANSWER_POSTED', default=5, cast=int)
POINTS_UPVOTE_RECEIVED = config('POINTS_UPVOTE_RECEIVED', default=10, cast=int)
POINTS_ACCEPTED_ANSWER = config('POINTS_ACCEPTED_ANSWER', default=20, cast=int)
POINTS_FAQ_CONTRIBUTION = config('POINTS_FAQ_CONTRIBUTION', default=15, cast=int)
POINTS_EDIT_ACCEPTED = config('POINTS_EDIT_ACCEPTED', default=10, cast=int)

# Gemini AI assistant
GEMINI_API_KEY = config('GEMINI_API_KEY', default='')
GEMINI_MODEL = config('GEMINI_MODEL', default='gemini-2.5-flash')

# Rich text sanitization
BLEACH_ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'a', 'h2', 'h3', 'blockquote', 'code', 'pre', 'span'
]
BLEACH_ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel'],
    'pre': ['class'],
    'code': ['class'],
    'p': ['style', 'class'],
    'span': ['style', 'class']
}

# Caching Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'faq-cache',
    }
}
REDIS_URL = config('REDIS_URL', default='')
if REDIS_URL:
    CACHES['default'] = {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'

# Allauth & Google OAuth Settings
SITE_ID = 1
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': True,
        'APP': {
            'client_id': config('GOOGLE_CLIENT_ID', default=''),
            'secret': config('GOOGLE_CLIENT_SECRET', default=''),
            'key': ''
        }
    }
}
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_VERIFICATION = 'optional'
SOCIALACCOUNT_LOGIN_ON_GET = True
