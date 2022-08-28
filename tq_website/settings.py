"""
Django settings for tq project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

import os
from os import environ

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from django.core.files.storage import Storage, FileSystemStorage

# Load environment if not present
if "TQ_DEBUG" not in environ.keys():
    from dotenv import load_dotenv
    load_dotenv()

ugettext = lambda s: s
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'logs')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(environ["TQ_DEBUG"].lower() == 'true')

# Application definition
INSTALLED_APPS = [
    'treebeard',
    'ckeditor',
    'hijack',  # Ability to impersonate other users
    # 'hijack.contrib.admin',
    'photologue',  # Django gallery plugin
    'sortedm2m',  # required for photologue
    'djangocms_text_ckeditor',  # note this needs to be above the 'cms' entry
    'cms',  # django CMS itself
    'menus',  # helper for model independent hierarchical website navigation
    'sekizai',  # for javascript and css management
    'djangocms_admin_style',  # You must add 'djangocms_admin_style' in the list before 'django.contrib.admin'.
    'django.contrib.messages',  # to enable messages framework (see :ref:`Enable messages <enable-messages>`)
    'django.contrib.humanize',
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
    'guardian',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'django_countries',
    'tq_website',
    'courses',
    'faq',
    'organisation',
    'events',
    'payment',
    'cms_plugins',
    'analytical',
    'rest_framework',
    'groups.apps.GroupsConfig',
    'email_system.apps.EmailSystemConfig',
    'partners.apps.PartnersConfig',
    'parler',
    'survey',
    'debug_toolbar',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
    'hijack.middleware.HijackUserMiddleware',
]

AUTHENTICATION_BACKENDS = (
    'guardian.backends.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

SITE_ID = 1  # Needed for DjangoCMS
DEPLOYMENT_DOMAIN = environ["TQ_DEPLOYMENT_DOMAIN"]
ALLOWED_HOSTS = environ["TQ_ALLOWED_HOSTS"].split(',')
CSRF_TRUSTED_ORIGINS = [f'https://{domain}' for domain in ALLOWED_HOSTS]
INTERNAL_IPS = ['127.0.0.1', '::1']  # loopback
USE_X_FORWARDED_HOST = True  # This should be set to true since we use NGINX as a proxy
X_FRAME_OPTIONS = 'SAMEORIGIN'  # In order for django CMS to function, X_FRAME_OPTIONS needs to be set to SAMEORIGIN
WSGI_APPLICATION = 'tq_website.wsgi.application'
ROOT_URLCONF = 'tq_website.urls'


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'de'
TIME_ZONE = 'CET'
USE_I18N = True
USE_L10N = True
USE_TZ = True

FORMAT_MODULE_PATH = [
    'tq_website.formats',
]


###############################################
# Configuration of allauth account management #
###############################################
ANONYMOUS_USER_ID = -1

LOGIN_URL = '/accounts/login/'
LOGOUT_URL = '/accounts/logout/'
# default redirect URL after login (if no GET parameter next is given)
LOGIN_REDIRECT_URL = "/profile/courses"

ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_USER_DISPLAY = lambda user: user.first_name if user.first_name else user.email
ACCOUNT_SIGNUP_FORM_CLASS = 'courses.forms.CustomSignupForm'
ACCOUNT_LOGOUT_ON_GET = True

# Password validation (native django, not django-allauth)
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        },
    }
]

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


S3_ENABLED = bool(environ["TQ_S3_ENABLED"].lower() == 'true')

# Define default storages
if S3_ENABLED:
    DEFAULT_FILE_STORAGE = 'tq_website.storages.MediaStorage'
    STATICFILES_STORAGE = 'tq_website.storages.StaticStorage'


# Use ACL of bucket
AWS_DEFAULT_ACL = None

# Use new signature version
AWS_S3_SIGNATURE_VERSION = "s3v4"

# Disable querystring auth (overridden by some storages)
AWS_QUERYSTRING_AUTH = False

# Media
S3_MEDIA_BUCKET = environ['TQ_S3_MEDIA_BUCKET']
S3_MEDIA_HOST = environ['TQ_S3_MEDIA_HOST']
S3_MEDIA_PORT = environ['TQ_S3_MEDIA_PORT']
S3_MEDIA_REGION = environ['TQ_S3_MEDIA_REGION']
S3_MEDIA_USE_SSL = bool(environ["TQ_S3_MEDIA_USE_SSL"].lower() == 'true')
S3_MEDIA_CUSTOM_DOMAIN = environ['TQ_S3_MEDIA_CUSTOM_DOMAIN']
S3_MEDIA_ACCESS_KEY = environ['TQ_S3_MEDIA_ACCESS_KEY']
S3_MEDIA_SECRET_KEY = environ['TQ_S3_MEDIA_SECRET_KEY']

# Static
S3_STATIC_BUCKET = environ['TQ_S3_STATIC_BUCKET']
S3_STATIC_HOST = environ['TQ_S3_STATIC_HOST']
S3_STATIC_PORT = environ['TQ_S3_STATIC_PORT']
S3_STATIC_REGION = environ['TQ_S3_STATIC_REGION']
S3_STATIC_USE_SSL = bool(environ["TQ_S3_STATIC_USE_SSL"].lower() == 'true')
S3_STATIC_CUSTOM_DOMAIN = environ['TQ_S3_STATIC_CUSTOM_DOMAIN']
S3_STATIC_ACCESS_KEY = environ['TQ_S3_STATIC_ACCESS_KEY']
S3_STATIC_SECRET_KEY = environ['TQ_S3_STATIC_SECRET_KEY']

# Finance
S3_FINANCE_BUCKET = environ['TQ_S3_FINANCE_BUCKET']
S3_FINANCE_HOST = environ['TQ_S3_FINANCE_HOST']
S3_FINANCE_PORT = environ['TQ_S3_FINANCE_PORT']
S3_FINANCE_REGION = environ['TQ_S3_FINANCE_REGION']
S3_FINANCE_USE_SSL = bool(environ["TQ_S3_FINANCE_USE_SSL"].lower() == 'true')
S3_FINANCE_CUSTOM_DOMAIN = environ['TQ_S3_FINANCE_CUSTOM_DOMAIN']
S3_FINANCE_ACCESS_KEY = environ['TQ_S3_FINANCE_ACCESS_KEY']
S3_FINANCE_SECRET_KEY = environ['TQ_S3_FINANCE_SECRET_KEY']


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
                [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.i18n",
                    "django.template.context_processors.media",
                    "django.template.context_processors.static",
                    "django.template.context_processors.tz",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                    "django.template.context_processors.request",
                    'sekizai.context_processors.sekizai',
                    'cms.context_processors.cms_settings',
                ]
        }
    },
]

############################################
# Configuration of djangocms-text-ckeditor #
############################################
# CKEDITOR_BASEPATH = "/static/ckeditor/ckeditor/"
CKEDITOR_UPLOAD_PATH = "uploads/"
# CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js' ## DO NOT LOAD twice since already loaded in template!
CKEDITOR_IMAGE_BACKEND = 'pillow'

ckeditor_toolbar_cms = [
    ['Undo', 'Redo'],
    ['cmsplugins', '-', 'ShowBlocks'],
    ['Format', 'Styles'],
    ['TextColor', 'BGColor', '-', 'PasteText', 'PasteFromWord'],
    ['Maximize'],
    '/',
    ['Source'],
    '/',
    ['Bold', 'Italic', 'Underline', '-', 'Subscript', 'Superscript', '-', 'RemoveFormat'],
    ['JustifyLeft', 'JustifyCenter', 'JustifyRight'],
    ['HorizontalRule'],
    ['NumberedList', 'BulletedList', 'Blockquote', '-', 'Outdent', 'Indent', '-', 'Table', 'Link', 'Unlink'],
]

# show cms plugins drop down only if used in cms
ckeditor_toolbar_htmlfield = ckeditor_toolbar_cms[:]
ckeditor_toolbar_htmlfield[1] = ['ShowBlocks']

# useful documentation about CKEditor:
# https://docs.ckeditor.com/#!/guide/dev_toolbarconcepts
# complete list of all available toolbar elements:
# https://ckeditor.com/forums/CKEditor/Complete-list-of-toolbar-items
# documentation for Django CMS plugin:
# https://pypi.python.org/pypi/djangocms-text-ckeditor/
CKEDITOR_SETTINGS = {
    'disableNativeSpellChecker': False,
    'language': 'en',
    'toolbar_CMS': ckeditor_toolbar_cms,
    'toolbar_HTMLField': ckeditor_toolbar_htmlfield,
    'skin': 'moono-lisa'
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

##################################################
# Configuration of post_office plugin und celery #
##################################################

# Celery
CELERY_ACCEPT_CONTENT = ['json', 'yaml']
CELERY_RESULT_BACKEND = 'django-db'
BROKER_URL = environ['TQ_REDIS_BROKER_URL']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# using post office as the default email backend
EMAIL_BACKEND = 'post_office.EmailBackend'

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = os.path.join(os.getcwd(), 'emails')

POST_OFFICE = {
    'BACKENDS': {
        # using djcelery's email backend as a backend for post office
        'default': EMAIL_BACKEND if DEBUG else 'djcelery_email.backends.CeleryEmailBackend',
    },
    'DEFAULT_PRIORITY': 'now'
}

###########
# Logging #
###########

# Note for DevOps: all the log files MUST be created before starting Django
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
        {'code': 'en', },
        {'code': 'de', },
    ),
    'default': {
        'fallbacks': ['de', 'en'],  # defaults to PARLER_DEFAULT_LANGUAGE_CODE
        'hide_untranslated': False,  # the default; let .active_translations() return fallbacks too.
    }
}

# Path for translation files
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

#################
# Debug Toolbar #
#################

DEBUG_TOOLBAR_PATCH_SETTINGS = False  # configure manually and do not let debug-toolbar autopatch my settings!
# Show toolbar whenever DEBUG is True. Workaround for dynamic IPs in a Docker environment (which would not be in INTERNAL_IPS)
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG,
}

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.history.HistoryPanel',
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
]


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = environ["TQ_SECRET_KEY"]

# Caching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'tq_website',
    } if DEBUG else {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': environ['TQ_REDIS_BROKER_URL'],
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    },
    'db': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'tq_cache_table',
    }
}

# Configure the email host to send mails from
EMAIL_HOST = environ["TQ_EMAIL_HOST"]
EMAIL_HOST_USER = environ["TQ_EMAIL_HOST_USER"]
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_PASSWORD = environ["TQ_EMAIL_HOST_PASSWORD"]
DEFAULT_FROM_EMAIL = environ["TQ_DEFAULT_FROM_EMAIL"]

EMAIL_ADDRESS_CONTACT = 'kontakt@tanzquotient.org'
EMAIL_ADDRESS_EVENTS = 'events@tanzquotient.org'
EMAIL_ADDRESS_FINANCES = 'finanzen@tanzquotient.org'
EMAIL_ADDRESS_COURSES = 'kurse@tanzquotient.org'
EMAIL_ADDRESS_COURSE_SUBSCRIPTIONS = 'anmeldungen@tanzquotient.org'
EMAIL_ADDRESS_COURSE_IT = 'informatik@tanzquotient.org'

# Database
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': environ["TQ_DB_HOST"],
        'PORT': environ["TQ_DB_PORT"],
        'NAME': environ['TQ_DB_NAME'],
        'USER': environ["TQ_DB_USER"],
        'PASSWORD': environ["TQ_DB_PASSWORD"],
    }
}

GOOGLE_ANALYTICS_PROPERTY_ID = environ["TQ_GOOGLE_ANALYTICS_PROPERTY_ID"]

# Postfinance Backend
FDS_HOST = 'fdsbc.post.ch'
FDS_USER = environ["TQ_FDS_USER"]
FDS_PRIVATE_KEY = environ["TQ_FDS_PRIVATE_KEY"]
FDS_DATA_PATH = 'fds_data'
FDS_PORT = 22

# Main Bank Account
PAYMENT_ACCOUNT = {
    'default': {
        'IBAN': environ["TQ_PAYMENT_ACCOUNT_IBAN"],
        'SWIFT': environ["TQ_PAYMENT_ACCOUNT_SWIFT"],
        'post_number': environ["TQ_PAYMENT_ACCOUNT_POST_NUMBER"],
        'recipient': ', '.join([environ["TQ_PAYMENT_ACCOUNT_RECIPIENT"],
                                environ["TQ_PAYMENT_ACCOUNT_RECIPIENT_ZIPCODE_CITY"]])
    }
}

# Logging
if not DEBUG:
    sentry_sdk.init(
        dsn="https://883ad6a3790e48aea0291f4a0d1d89c4@sentry.io/124755",
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        environment=environ["TQ_ENVIRONMENT"],
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True
    )
