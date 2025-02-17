import environ
from pathlib import Path
import os
import dj_database_url

env = environ.Env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

IS_HEROKU_APP = "DYNO" in os.environ and not "CI" in os.environ

GOOGLE_MAPS_API_KEY = env('GOOGLE_MAPS_API_KEY', default=None)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/


SECRET_KEY = env('SECRET_KEY', default=None)

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = env.bool('DEBUG', default=False)

if IS_HEROKU_APP:  # Only enable SSL related settings on Heroku
    DEBUG = False  # Make sure debug is False in production
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    ALLOWED_HOSTS = ['patrons.love', 'www.patrons.love', '.herokuapp.com', 'dev.patrons.love'] 
else:
    # Development settings (locally)
    DEBUG = True
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']

PRINTFUL_REDIRECT_URL = 'https://patrons.love/{business_subdirectory}/callback' 

PRINTFUL_CLIENT_ID = env('PRINTFUL_CLIENT_ID', default=None)

if not DEBUG:
    BASIC_AUTH_USERNAME = env('BASIC_AUTH_USERNAME', default=None)
    BASIC_AUTH_PASSWORD = env('BASIC_AUTH_PASSWORD', default=None)

ACCOUNT_TEMPLATE_DIR = os.path.join(BASE_DIR, 'restaurants', 'templates', 'account')
# Application definition


ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.herokuapp.com',
    'dev.patrons.love',
    'www.patrons.love',
    '.patrons.love'
]



CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'https://localhost:8000',
    'http://127.0.0.1:8000',
    'https://127.0.0.1:8000',
    'https://*.herokuapp.com',
    'https://dev.patrons.love',
    # 'https://patrons.love',
]



INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',
    'anymail',
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
    'storages',
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
            'profile',
            'email',
            'https://www.googleapis.com/auth/business.manage',
        ],
        'APP': {
            'client_id': env('CLIENT_ID', default=None),
            'secret': env('GOOGLE_SECRET', default=None),
            'key': '',
        }
    }
}

# Add environment-specific AUTH_PARAMS
if DEBUG:
    SOCIALACCOUNT_PROVIDERS['AUTH_PARAMS'] = {
        'access_type': 'offline',
        'prompt': 'consent',
    }
else:
    SOCIALACCOUNT_PROVIDERS['AUTH_PARAMS'] = {
        'access_type': 'online',
    }


SOCIALACCOUNT_STORE_TOKENS = True
SOCIALACCOUNT_LOGIN_ON_GET = True

# adapters for username

ACCOUNT_ADAPTER = 'restaurants.adapters.CustomAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'restaurants.adapters.CustomSocialAccountAdapter'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware",
    'restaurants.middleware.ClearMessagesMiddleware', 
    'restaurants.middleware.JavaScriptMimeTypeMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'restaurants.middleware.BasicAuthMiddleware', 
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
# Remove or comment out this line since we'll generate usernames
# ACCOUNT_USER_MODEL_USERNAME_FIELD = None
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_EMAIL_REQUIRED = True
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

# Mailgun
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')

ANYMAIL = {
    "MAILGUN_API_KEY": env('MAILGUN_API_KEY', default=None),
    "MAILGUN_SENDER_DOMAIN": "admin.patrons.love"
}
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = '127.0.0.1'
    EMAIL_PORT = 1025
    EMAIL_HOST_USER = ''
    EMAIL_HOST_PASSWORD = ''
    EMAIL_USE_TLS = False
    DEFAULT_FROM_EMAIL = 'development@localhost'
else:
    # Production using Mailgun
    EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'
    DEFAULT_FROM_EMAIL = 'noreply@admin.patrons.love'
    SERVER_EMAIL = "noreply@admin.patrons.love"


# Login/out URLs

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'


ACCOUNT_TEMPLATE_EXTENSION = 'html'

if IS_HEROKU_APP:
    DATABASES = {
        "default": dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True,
        ),
    }
else:
    DATABASES = {
        "default": {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': env('DB_NAME'),
            'USER': env('DB_USER'),
            'PASSWORD': env('DB_PASSWORD'),
            'HOST': env('DB_HOST'),
            'PORT': env('DB_PORT'),
        }
    }

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

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'restaurants/static/dist'),
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

#storage settings
if IS_HEROKU_APP:
    # AWS S3 Settings
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = 'us-east-1'  # or your region
    AWS_DEFAULT_ACL = 'public-read'  # Make files public by default
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

    
    # Production storage settings
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
    
    # Media files
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',  # 24 hours
    }
    AWS_QUERYSTRING_AUTH = False  # Disable query parameter authentication
    AWS_S3_FILE_OVERWRITE = False 
    
else:
    # Development storage settings
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
    if os.path.exists(os.path.join(BASE_DIR, "static")):
        STATICFILES_DIRS = [
            os.path.join(BASE_DIR, "static"),
        ]
    
    # Local media files
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

ADMIN_EMAIL = 'admin@example.com'

FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB


# Only set up logging for local development

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
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 3,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        'restaurants': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': True,
        },
        'django': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': True,
        },
        'django.server': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

