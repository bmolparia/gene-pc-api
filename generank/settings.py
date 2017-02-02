""" Django settings for generank project. """

import os, sys
from datetime import timedelta

env = os.environ.get('ENVIRONMENT', 'dev').lower()
USE_SSL = (os.environ.get('USE_SSL', '').lower() == 'true')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

SECRET_KEY = os.environ.get('SECRET_KEY', None)

DEBUG = (env != 'prod')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '.scripps.edu').split(':')

if DEBUG:
    CORS_ORIGIN_ALLOW_ALL = True
else:
    CORS_ORIGIN_WHITELIST = (
        'generank.scripps.edu',
        'stsi01.scripps.edu',
    )

# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',

    'rest_framework',
    'oauth2_provider',
    'push_notifications',

    'generank.api',
    'generank.twentythreeandme',
    'generank.compute',
    'generank.reporting',
]

if DEBUG:
    INSTALLED_APPS += [
        'debug_toolbar',
        'django_nose',
    ]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.AllowAny',),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.ext.rest_framework.OAuth2Authentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
    )
}

if not DEBUG:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
        'rest_framework.renderers.JSONRenderer',
    )

OAUTH2_PROVIDER = {
    # this is the list of available scopes
    'SCOPES': {'read': 'Read scope', 'write': 'Write scope', 'groups': 'Access to your groups'}
}

PUSH_NOTIFICATIONS_SETTINGS = {
    "GCM_API_KEY": os.environ.get('GCM_API_KEY', None),
    "APNS_CERTIFICATE": os.environ.get('APNS_CERTIFICATE', None),
}

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'generank/templates'
        ],
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

WSGI_APPLICATION = 'generank.wsgi.application'


# Security
SECURE_HSTS_SECONDS = 518400
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_FRAME_DENY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_HTTPONLY = True

if USE_SSL:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True

if not DEBUG and USE_SSL:
    # See notes at https://docs.djangoproject.com/en/1.10/ref/settings/
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
if env == 'test' or env == 'prod':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DATABASE_NAME', None),
            'USER': os.environ.get('POSTGRES_USER', None),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', None),
            'HOST': os.environ.get('POSTGRES_HOST', None),
            'PORT': '5432',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

AUTH_USER_MODEL = 'api.User'

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.environ.get('STATIC_ROOT', None)
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]

# File storage options

DATA_URL = '/data/'
DATA_STORAGE = os.environ.get('DATA_STORAGE', os.path.join(BASE_DIR, "data"))

TTM_RAW_URL = '/data/23andme/raw/'
TTM_RAW_STORAGE = os.environ.get('TTM_RAW_STORAGE', os.path.join(DATA_STORAGE, '23andme', 'raw'))

TTM_CONVERTED_URL = '/data/23andme/converted/'
TTM_CONVERTED_STORAGE = os.environ.get('TTM_CONVERTED_STORAGE', os.path.join(DATA_STORAGE, '23andme', 'converted'))

CONSENT_FILE_URL = '/data/consent/'
CONSENT_FILE_LOCATION = os.environ.get('CONSENT_FILE_LOCATION', os.path.join(DATA_STORAGE, 'consent'))

# Loaded URLs

ROOT_URLCONF = 'generank.urls'

# Sending Email

EMAIL_HOST = os.environ.get('EMAIL_HOST', None)
EMAIL_PORT = os.environ.get('EMAIL_PORT', None)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', None)
EMAIL_HOST_PASSWORD  = os.environ.get('EMAIL_HOST_PASSWORD ', None)
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
REGISTER_EMAIL_SUBJECT = 'Register your Account with MyGeneRank'

# 23andMe Settings

TTM_CLIENT_ID = os.environ['TTM_CLIENT_ID']
TTM_CLIENT_SECRET = os.environ['TTM_CLIENT_SECRET']
TTM_GRANT_TYPE = os.environ['TTM_GRANT_TYPE']
TTM_REDIRECT_URI = os.environ['TTM_REDIRECT_URI']
TTM_SCOPE = os.environ['TTM_SCOPE']

# Logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        'django': {
            'handlers': ['file', 'console', 'mail_admins'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': True,
        },

        # Send email to admins for any request errors.
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    }
}

ADMINS = [
    ('admin', os.getenv('ADMIN_EMAIL', None)),
]

# Celery Settings
try:
    BROKER_URL = os.environ['BROKER_URL']
    CELERY_RESULT_BACKEND = os.environ['BACKEND_URL']
    #CELERYD_PREFETCH_MULTIPLIER = os.environ.get('CELERYD_PREFETCH_MULTIPLIER', 1)
    #CELERY_ACKS_LATE = True
except KeyError:
    CELERY_ALWAYS_EAGER = True
    CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_RESULT_EXPIRES = timedelta(minutes=15)

CELERY_IMPORTS = [
    'generank.compute.tasks.cad'
]

# Celery Periodic Tasks

FOLLOWUP_TIME = 1 if DEBUG else int(os.environ.get('FOLLOWUP_TIME', 180))
CELERYBEAT_SCHEDULE = {
    'add-new-activity-status-for-follow-up-survey': {
        'task': 'generank.api.tasks.send_followup_survey_to_users',
        'schedule': timedelta(days=1),
    },
}

CELERY_TIMEZONE = 'UTC'

# Fabric settings

REMOTE_HOSTS =  ['fabric@137.131.231.252']

# Survey Tasks

PHENOTYPE_SURVEY_ID = "PhenotypeSurveyTask"
GENOTYPE_AUTH_SURVEY_ID = "TwentyThreeAndMeLoginTask"
POST_CAD_RESULTS_SURVEY_ID = "PostCADResultsSurveyTask"
POST_CAD_6MO_SURVEY_ID = "CADFollowUpSurveyTask"
