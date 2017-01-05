"""
Django settings for tq project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP
from django.utils.translation import ugettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

import logging

ugettext = lambda s: s
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'logs')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/


ALLOWED_HOSTS = [
    # with . at beginning allows domain and subdomains
    # with . at end allows FQDN
    '.tq.ethz.ch.',
    '.tq.vseth.ch.',
    '.tq.vseth.ethz.ch.',
    '.tanzquotient.vseth.ethz.ch.',
    '.tanzquotient.org',
    '46.231.204.51',
    '192.168.99.100',
    '127.0.0.1', 'localhost',
]
# This should be set to true since we use NGINX as a proxy
USE_X_FORWARDED_HOST = True

# Application definition

INSTALLED_APPS = [
    'raven.contrib.django.raven_compat',
    'treebeard',
    'djangocms_text_ckeditor',  # note this needs to be above the 'cms' entry
    'filer',
    'easy_thumbnails',
    'djangocms_googlemap',
    'djangocms_inherit',
    'djangocms_link',
    'cmsplugin_filer_link',
    'cmsplugin_filer_image',
    'cms',  # django CMS itself
    'mptt',  # utilities for implementing a tree
    'menus',  # helper for model independent hierarchical website navigation
    'sekizai',  # for javascript and css management
    'djangocms_admin_style',
    'bootstrap3',
    # for the admin skin. You **must** add 'djangocms_admin_style' in the list **before** 'django.contrib.admin'.
    'django.contrib.messages',  # to enable messages framework (see :ref:`Enable messages <enable-messages>`)
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'reversion',
    'django_celery_beat',
    'django_celery_results',
    'djcelery_email',
    'post_office',
    'absolute',
    'daterange_filter',
    'guardian',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'tq_website',
    'courses',
    'faq',
    'organisation',
    'events',
    'payment',
    'cms_plugins',
    'analytical',
    'rest_framework',
    'parler',
    'survey',
    'debug_toolbar',
]

MIDDLEWARE_CLASSES = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'guardian.backends.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

SITE_ID = 1

ROOT_URLCONF = 'tq_website.urls'

WSGI_APPLICATION = 'tq_website.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'de'

TIME_ZONE = 'CET'

USE_I18N = True

USE_L10N = True

USE_TZ = True

INTERNAL_IPS = ['127.0.0.1', '172.21.0.1', '::1']

###############################################
# Configuration of allauth account management #
###############################################
ANONYMOUS_USER_ID = -1

LOGIN_URL = '/accounts/login/'
LOGOUT_URL = '/accounts/logout/'
# default redirect URL after login (if no GET parameter next is given)
LOGIN_REDIRECT_URL = "/accounts/email"

ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_EMAIL_SUBJECT_PREFIX = 'TQ '
# ACCOUNT_LOGIN_ON_PASSWORD_RESET=True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/login'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_SESSION_REMEMBER = False
ACCOUNT_USER_DISPLAY = lambda user: user.first_name if user.first_name else user.email
ACCOUNT_SIGNUP_FORM_CLASS = 'courses.forms.CustomSignupForm'
ACCOUNT_LOGOUT_ON_GET = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

# general cross-used static files
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

STATIC_ROOT = os.path.join(BASE_DIR, "collected_static")
STATIC_URL = '/static/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
)

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = '/media/'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, "templates"),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors':
                TCP + [
                    "django.contrib.auth.context_processors.auth",
                    "django.core.context_processors.debug",
                    "django.core.context_processors.i18n",
                    "django.core.context_processors.media",
                    "django.core.context_processors.static",
                    "django.core.context_processors.tz",
                    "django.contrib.messages.context_processors.messages",
                    "django.template.context_processors.request",
                    'sekizai.context_processors.sekizai',
                    'cms.context_processors.cms_settings',
                    'absolute.context_processors.absolute',
                ]
        }
    },
]

############################################
# Configuration of djangocms-text-ckeditor #
############################################
CKEDITOR_UPLOAD_PATH = "uploads/"
# CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js' ## DO NOT LOAD twice since already loaded in template!
CKEDITOR_IMAGE_BACKEND = 'pillow'

CKEDITOR_SETTINGS = {
    'language': 'en',
    'toolbar_HTMLField': [
        ['Undo', 'Redo'],
        ['ShowBlocks'],
        ['Format', 'Styles'],
        ['Link', 'Unlink'],
        ['Source', ],
    ],
    'skin': 'moono',
}

###############################
# Configuration of django-cms #
###############################
CMS_TEMPLATES = (
    ('template_basic.html', 'Basic Template'),
    ('template_sidebar.html', 'Sidebar Template'),
)

LANGUAGES = [
    ('de', ugettext('Deutsch')),
    ('en', ugettext('English')),
]

PARLER_LANGUAGES = {
    None: (
        {'code': 'de',},
        {'code': 'en',},
    ),
}

CMS_LANGUAGES = {
    1: [
        {
            'code': 'de',
            'name': ugettext('Deutsch'),
            'fallbacks': ['en', ],
            'public': True,
            'hide_untranslated': False,
            'redirect_on_fallback': False,
        },
        {
            'code': 'en',
            'name': ugettext('English'),
            'fallbacks': ['de', ],
            'public': True,
            'hide_untranslated': False,
            'redirect_on_fallback': False,
        },
    ],
    'default': {
        'fallbacks': ['en', 'de', ],
        'redirect_on_fallback': True,
        'public': True,
        'hide_untranslated': False,
    }
}

CMS_PLACEHOLDER_CONF = {
    'cms_content': {
        'name': ugettext('Main content'),
        'language_fallback': True,
    },
    'side_content': {
        'name': ugettext('Side content'),
        'language_fallback': True,
    },
    'title': {
        'name': ugettext('Title'),
        'language_fallback': True,
        'plugins': ['PageTitlePlugin'],
        'limits': {
            'PageTitlePlugin': 1,
        },
        'default_plugins': [
            {
                'plugin_type': 'PageTitlePlugin',
                'values': {},
            },
        ],
        'child_classes': {
            'PageTitlePlugin': ['ButtonPlugin', ],
        },
        'parent_classes': {
            'ButtonPlugin': ['PageTitlePlugin'],
        },
    },
}

##########################
# Configuration of filer #
##########################
THUMBNAIL_HIGH_RESOLUTION = True

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    # 'easy_thumbnails.processors.scale_and_crop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)

####################################
# Configuration of cmsplugin-filer #
####################################
TEXT_SAVE_IMAGE_FUNCTION = 'cmsplugin_filer_image.integrations.ckeditor.create_image_plugin'

##################################################
# Configuration of post_office plugin und celery #
##################################################

# Celery
CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']
CELERY_RESULT_BACKEND = 'django-db'
BROKER_URL = "redis://redis/"
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# using post office as the default email backend 
EMAIL_BACKEND = 'post_office.EmailBackend'

POST_OFFICE = {
    'BACKENDS': {
        # using djcelery's email backend as a backend for post office
        'default': 'djcelery_email.backends.CeleryEmailBackend',
    },
    'DEFAULT_PRIORITY': 'now'
}

###########
# Logging #
###########

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'file_django': {
            'level': 'WARN',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'django.log'),
            'maxBytes': 50000000,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'file_tq': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'tq.log'),
            'maxBytes': 50000000,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'file_payment': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'payment.log'),
        },
        'file_errors': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'errors.log'),
            'maxBytes': 50000000,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        # this top level logger logs ALL messages
        '': {
            'handlers': ['mail_admins', 'file_errors'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'tq': {
            'handlers': ['file_tq', 'console'],
            'level': 'DEBUG',
        },
        'payment': {
            'level': 'DEBUG',
            'handlers': ['console', 'file_payment', ],
        },
        'django': {
            'handlers': ['file_django', 'console'],
            'level': 'INFO',
        },
    }
}

##################
# REST FRAMEWORK #
##################
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

##########
# PARLER #
##########
PARLER_LANGUAGES = {
    SITE_ID: (
        {'code': 'en',},
        {'code': 'de',},
    ),
    'default': {
        'fallbacks': ['de'],  # defaults to PARLER_DEFAULT_LANGUAGE_CODE
        'hide_untranslated': False,  # the default; let .active_translations() return fallbacks too.
    }
}

# Path for translation files
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

# Caching

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'memcached:{}'.format(os.environ.get("TQ_MEMCACHED_PORT", '')),
    },
    'db': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'tq_cache_table',
    }
}

#################
# Debug Toolbar #
#################

DEBUG_TOOLBAR_PATCH_SETTINGS = False  # configure manually and do not let debug-toolbar autopatch my settings!

# Internal IPs for Debug Toolbar
INTERNAL_IPS = ['127.0.0.1', '192.168.99.100', '192.168.99.1']

# import local settings (includes secrets, thats why settings_local MUST NOT BE UNDER VERSION CONTROL!!!)
from .settings_local import *

import os
import raven

RAVEN_CONFIG = {
    'dsn': 'https://883ad6a3790e48aea0291f4a0d1d89c4:339fab1993244b4e9d414ebcef70cee0@sentry.io/124755',
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    'release': raven.fetch_git_sha(os.path.dirname(os.pardir)),
}