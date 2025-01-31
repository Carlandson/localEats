import environ
from pathlib import Path
import os

env = environ.Env()
environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


GOOGLE_MAPS_API_KEY = env('GOOGLE_MAPS_API_KEY', default=None)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/


SECRET_KEY = env('SECRET_KEY', default=None)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False)

PRINTFUL_REDIRECT_URI = 'https://17115eed1538e7.lhr.life/callback' 

PRINTFUL_CLIENT_ID = env('PRINTFUL_CLIENT_ID', default=None)



ACCOUNT_TEMPLATE_DIR = os.path.join(BASE_DIR, 'restaurants', 'templates', 'account')
# Application definition
NGROK_URL = env('NGROK_URL', default=None)

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '17115eed1538e7.lhr.life'
]


CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'https://localhost:8000',
    'http://127.0.0.1:8000',
    'https://127.0.0.1:8000',
    'https://17115eed1538e7.lhr.life',
    'https://17115eed1538e7.lhr.life'
]



if NGROK_URL:
    ALLOWED_HOSTS.append(NGROK_URL)

INSTALLED_APPS = [
    'restaurants',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_google_maps',
    'tailwind',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'widget_tweaks',
    'phonenumber_field',
    'crispy_forms',
    'crispy_tailwind',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'https://www.googleapis.com/auth/userinfo.profile',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/business.manage',
        ],
        'AUTH_PARAMS': {
            'access_type': 'offline',
            'prompt': 'consent',
        },
        'APP' : {
            'client_id': env('CLIENT_ID', default=None),
            'secret': env('GOOGLE_SECRET', default=None),
            'key': '',
        }

    }
}

SOCIALACCOUNT_STORE_TOKENS = True
SOCIALACCOUNT_LOGIN_ON_GET = True

# adapters for username

ACCOUNT_ADAPTER = 'restaurants.adapters.CustomAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'restaurants.adapters.CustomSocialAccountAdapter'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware",
    'restaurants.middleware.ClearMessagesMiddleware', 
    'restaurants.middleware.JavaScriptMimeTypeMiddleware',
]

# WebP settings
WEBP_CONVERT_MEDIA = True
WEBP_QUALITY = 80

ROOT_URLCONF = 'localeats.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'restaurants', 'templates'),
            os.path.join(BASE_DIR, 'restaurants', 'templates', 'account'),  # Add this line
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'restaurants.context_processors.user_data',
                'restaurants.context_processors.debug_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'localeats.wsgi.application'

# AllAuth settings
ACCOUNT_FORMS = {'signup': 'restaurants.forms.CustomSignupForm'}
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/accounts/login/'
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = '/'
ACCOUNT_EMAIL_SUBJECT_PREFIX = '[LocalEats] '
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_RATE_LIMITS = {
    'confirm_email': '3/h',  # 3 per hour
}

# Mailpit
if DEBUG and not env.bool('USE_MAILGUN', default=False):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = '127.0.0.1'
    EMAIL_PORT = 1025
    EMAIL_HOST_USER = ''
    EMAIL_HOST_PASSWORD = ''
    EMAIL_USE_TLS = False
    DEFAULT_FROM_EMAIL = 'development@localhost'
else:
    EMAIL_BACKEND = 'django_mailgun.MailgunBackend'
    MAILGUN_ACCESS_KEY = env('MAILGUN_ACCESS_KEY', default=None)
    MAILGUN_SERVER_NAME = env('MAILGUN_SERVER_NAME', default=None)
    DEFAULT_FROM_EMAIL = f'noreply@{MAILGUN_SERVER_NAME}'
# Login/out URLs

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'


ACCOUNT_TEMPLATE_EXTENSION = 'html'
# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases


# SQLITE3
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'localeats',
        'USER': 'postgres',
        'PASSWORD': '123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'restaurants/static/dist'),
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

ADMIN_EMAIL = 'admin@example.com'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',  # Changed from DEBUG to INFO
            'class': 'logging.StreamHandler',
            'formatter': 'simple',  # Changed to simple for console
        },
        'file': {
            'level': 'WARNING',  # Changed from DEBUG to WARNING
            'class': 'logging.handlers.RotatingFileHandler',  # Changed to RotatingFileHandler
            'filename': os.path.join(BASE_DIR, 'debug.log'),
            'maxBytes': 5 * 1024 * 1024,  # 5 MB
            'backupCount': 3,  # Keep 3 backup files
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        'restaurants': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',  # Changed from DEBUG to WARNING
            'propagate': True,
        },
        'django': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',  # Changed from INFO to WARNING
            'propagate': True,
        },
        'django.server': {  # Added to reduce server logs
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.db.backends': {  # Added to reduce SQL query logs
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# If you want to switch between development and production configs:
if not DEBUG:
    # Production logging settings
    LOGGING['handlers']['file']['filename'] = '/var/log/localeats/error.log'
    LOGGING['handlers']['file']['level'] = 'ERROR'
    for logger in LOGGING['loggers'].values():
        logger['level'] = 'ERROR'
        logger['handlers'] = ['file']