"""
Django settings for waves_core project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""
from __future__ import unicode_literals
import os
import logging.config
import environ
from django.contrib import messages


env = environ.Env()
if os.path.isfile(os.path.join(os.path.dirname(__file__), 'local.env')):
    environ.Env.read_env(os.path.join(os.path.dirname(__file__), 'local.env'))

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('SECRET_KEY', '0jmf=ngd^2**h3km5@#&w21%hlj9kos($2=igsqh8-38_9g1$1')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', True)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

# Application definition
INSTALLED_APPS = (
    'polymorphic',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'waves.wcore',
    'waves.authentication',
    'crispy_forms',
    'rest_framework',
    'corsheaders',
    'adminsortable2'
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'waves_core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
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

WSGI_APPLICATION = 'waves_core.wsgi.application'

# DATABASE configuration
DATABASES = {
    'default': env.db(default='sqlite:///' + BASE_DIR + '/db.sqlite3'),
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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

LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
MEDIA_ROOT = env.str('MEDIA_ROOT', os.path.join(BASE_DIR, 'media'))
MEDIA_URL = "/media/"
STATIC_ROOT = env.str('STATIC_ROOT', os.path.join(BASE_DIR, 'staticfiles'))

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "waves", "wcore", "static"),
    os.path.join(BASE_DIR, "static")
]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

CRISPY_TEMPLATE_PACK = 'bootstrap3'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(levelname)s][%(asctime)s][%(name)s.%(funcName)s:%(lineno)s] - %(message)s',
            'datefmt': "%H:%M:%S"
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'log_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'waves.log'),
            'formatter': 'verbose',
            'backupCount': 10,
            'maxBytes': 1024 * 1024 * 5
        },
    },

    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'WARNING',
        },
        'waves': {
            'handlers': ['log_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },

    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'waves.authentication.auth.TokenAuthentication',
        'waves.authentication.auth.ApiKeyAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ]
}
ALLOWED_TEMPLATE_PACKS = ['bootstrap3', 'bootstrap4']

MESSAGE_TAGS = {
    messages.ERROR: 'error'
}

WAVES_CORE = {
}
# SECURITY
CORS_ORIGIN_WHITELIST = env.list('CORS_ORIGIN_WHITELIST', default=['localhost'])
CORS_ORIGIN_REGEX_WHITELIST = env.list('CORS_ORIGIN_REGEX_WHITELIST', default=['localhost:*'])
CORS_ORIGIN_ALLOW_ALL = env.bool('CORS_ORIGIN_ALLOW_ALL', False)

FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755
FILE_UPLOAD_PERMISSIONS = 0o775

# EMAILS
DEFAULT_FROM_EMAIL = 'WAVES <waves-demo@atgc-montpellier.fr>'
CONTACT_EMAIL = env.str('CONTACT_EMAIL', DEFAULT_FROM_EMAIL)

# WAVES
ADAPTORS_DEFAULT_CLASSES = (
        'waves.wcore.adaptors.shell.SshShellAdaptor',
        'waves.wcore.adaptors.cluster.LocalClusterAdaptor',
        'waves.wcore.adaptors.shell.SshKeyShellAdaptor',
        'waves.wcore.adaptors.shell.LocalShellAdaptor',
        'waves.wcore.adaptors.cluster.SshClusterAdaptor',
        'waves.wcore.adaptors.cluster.SshKeyClusterAdaptor',
    )
WAVES_CORE = {
    'ACCOUNT_ACTIVATION_DAYS': 14,
    'ADMIN_EMAIL': env.str('ADMIN_EMAIL', 'admin@waves.atgc-montpellier.fr'),
    'DATA_ROOT': env.str('WAVES_DATA_ROOT', os.path.join(BASE_DIR, 'data')),
    'JOB_LOG_LEVEL': env.str('JOB_LOG_LEVEL', logging.DEBUG),
    'JOB_BASE_DIR': env.str('WAVES_JOB_BASE_DIR', os.path.join(BASE_DIR, 'data', 'jobs')),
    'BINARIES_DIR': env.str('WAVES_BINARIES_DIR', os.path.join(BASE_DIR, 'data', 'bin')),
    'SAMPLE_DIR': env.str('WAVES_SAMPLE_DIR', os.path.join(BASE_DIR, 'data', 'sample')),
    'KEEP_ANONYMOUS_JOBS': env.int('KEEP_ANONYMOUS_JOBS', 2),
    'KEEP_REGISTERED_JOBS': env.int('KEEP_REGISTERED_JOBS', 2),
    'ALLOW_JOB_SUBMISSION': env.bool('ALLOW_JOB_SUBMISSION', True),
    'APP_NAME': env.str('APP_NAME', 'WAVES CORE'),
    'SERVICES_EMAIL': env.str('SERVICES_EMAIL', 'contact@atgc-montpellier.fr'),
    'ADAPTORS_CLASSES': env.tuple('ADAPTORS_CLASSES', default=ADAPTORS_DEFAULT_CLASSES),
}

# CONF EMAIL
EMAIL_CONFIG = env.email_url('EMAIL_URL', default='smtp://dummyuser@dummyhost:dummypassword@localhost:25')
vars().update(EMAIL_CONFIG)

MANAGERS = env.tuple('MANAGERS', default=[('Vincent Lefort', 'vincent.lefort@lirmm.fr')])

LOG_DIR = env.str("LOG_DIR", os.path.join(BASE_DIR, 'logs'))
APP_LOG_LEVEL = env.str("APP_LOG_LEVEL", 'WARNING')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(levelname)s][%(asctime)s][%(name)s.%(funcName)s:%(lineno)s] - %(message)s',
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'log_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'waves-app.log'),
            'formatter': 'verbose',
            'backupCount': 10,
            'maxBytes': 1024*1024*5
        },
    },

    'loggers': {
        'django': {
            'handlers': ['log_file', 'console'],
            'propagate': True,
            'level': 'WARNING',
        },
        'waves': {
            'handlers': ['log_file'],
            'level': 'WARNING',
            'propagate': True,
        },
    }
}
