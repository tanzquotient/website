"""
Django settings for tq project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP,\
    MEDIA_ROOT, STATIC_ROOT

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '65nyt75%e(kjqswhz@di(uqx$k)*gm^uv@%n64^6yue1@_lwgu'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, "templates"),
) 

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'grappelli.dashboard',
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tinymce',
    'tq_website',
    'courses',
    'faq',
    'organisation',
    'events',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'tq_website.urls'

WSGI_APPLICATION = 'tq_website.wsgi.application'

ALLOWED_HOSTS = [
    # with . at beginning allows domain and subdomains
    # with . at end allows FQDN
    '.tq.ethz.ch.',  
    '.tq.vseth.ch.',
    '.tq.vseth.ethz.ch.',
    '.tanzquotient.vseth.ethz.ch.',
]

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'localhost',
        'NAME': 'tq_website',
        'USER': 'root',
        'PASSWORD': 'eesseell',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'de-ch'

TIME_ZONE = 'CET'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# default redirect URL after login (if no GET paramter next is given)
LOGIN_REDIRECT_URL = "/admin/"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

# app specific static files
STATIC_URL = '/static/' 
# general cross-used static files
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

STATIC_ROOT = './collected_static/' # TODO maybe change this to absolute path (saver)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
)

MEDIA_ROOT = './media/' # TODO maybe change this to absolute path (saver)
MEDIA_URL = '/media/'

TEMPLATE_CONTEXT_PROCESSORS = TCP + (
"django.contrib.auth.context_processors.auth",
"django.core.context_processors.debug",
"django.core.context_processors.i18n",
"django.core.context_processors.media",
"django.core.context_processors.static",
"django.core.context_processors.tz",
"django.contrib.messages.context_processors.messages",
"django.core.context_processors.request",
)

GRAPPELLI_ADMIN_TITLE = "TQ Backend"

# Grappelli dashboard location
GRAPPELLI_INDEX_DASHBOARD = 'dashboard.CustomIndexDashboard'

# Grappelli autocomplete for user model
GRAPPELLI_AUTOCOMPLETE_SEARCH_FIELDS = {
    "django.contrib.auth": {
        "User": ("id__iexact","username__icontains", "first_name__icontains","last_name__icontains","email__icontains",)
    }
}

TINYMCE_DEFAULT_CONFIG = {
    'plugins' : '',
    'width': 600,
    'height': 450,
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
#         'logfile': {
#             'level':'DEBUG',
#             'class':'logging.handlers.RotatingFileHandler',
#             'filename': BASE_DIR + "/logfile",
#             'maxBytes': 50000,
#             'backupCount': 2,
#             'formatter': 'standard',
#         },
        'console':{
            'level':'INFO',
            'class':'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'handlers':['console'],
            'propagate': True,
            'level':'WARN',
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'courses': {
            'handlers': ['console'], # better: ['console', 'logfile']
            'level': 'DEBUG',
        },
    }
}
