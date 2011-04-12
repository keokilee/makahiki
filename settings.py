## -*- coding: utf-8 -*-

# settings.py
# This file contains system level settings.
# Settings include database, time zone, authentication, and installed apps.
# New settings should not be added here.

import os.path
import posixpath
import pinax
import logging

PINAX_ROOT = os.path.abspath(os.path.dirname(pinax.__file__))
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# tells Pinax to use the default theme
PINAX_THEME = 'default'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# tells Pinax to serve media through django.views.static.serve.
SERVE_MEDIA = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'    # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = 'dev.db'       # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Generates XML reports for the Django tests.
# Requires http://pypi.python.org/pypi/unittest-xml-reporting/1.0.3
# TEST_RUNNER = 'xmlrunner.extra.djangotestrunner.run_tests'
# TEST_OUTPUT_DESCRIPTIONS = True
# TEST_OUTPUT_DIR = "log"

# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Pacific/Honolulu'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'site_media', 'media')

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/site_media/media/'

# Location to save the files used for confirming activities (if enabled).
# Location is relative to MEDIA_ROOT.
ACTIVITY_FILE_DIR = "activities"

# Absolute path to the directory that holds static files like app media.
# Example: "/home/media/media.lawrence.com/apps/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'site_media', 'static')

# URL that handles the static files like app media.
# Example: "http://media.lawrence.com"
STATIC_URL = '/site_media/static/'

# Additional directories which hold static files
STATICFILES_DIRS = (
    ('makahiki', os.path.join(PROJECT_ROOT, 'media')),
    ('pinax', os.path.join(PINAX_ROOT, 'media', PINAX_THEME)),
)

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = posixpath.join(STATIC_URL, "admin/")

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'o7@06j^w^ptgaj7)$1meped4%^m^!%mae9ki#g6zx_!(11qcu+'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
    # 'dbtemplates.loader.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'account.middleware.LocaleMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'pinax.middleware.security.HideSensistiveFieldsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.csrf.CsrfResponseMiddleware',
    'lib.django_cas.middleware.CASMiddleware',
    'components.makahiki_profiles.middleware.LoginTrackingMiddleware',
    'pages.home.middleware.CheckSetupMiddleware',
	'components.logging.middleware.LoggingMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'components.makahiki_auth.models.MakahikiCASBackend',
)

ROOT_URLCONF = 'makahiki.urls'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), "templates"),
    os.path.join(PINAX_ROOT, "templates", PINAX_THEME),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    'django.contrib.messages.context_processors.messages',
    "pinax.core.context_processors.pinax_settings",
    "notification.context_processors.notification",
    # "account.context_processors.openid",
    "account.context_processors.account",
    
    "components.makahiki_base.context_processors.competition",
    "components.makahiki_themes.context_processors.css_selector",
)

INSTALLED_APPS = (
    # Makahiki pages
    'pages.view_activities',
    'pages.view_profile',
    'pages.view_energy',
    'pages.view_help',
    'pages.home',
    'pages.landing',
    'pages.news',
    'pages.mobile',
    'pages.view_prizes',
    
    # Makahiki components
    'components.activities',
    'components.api',
    'lib.django_cas', # Placed here so that it registers as an app during testing.
    'components.floors',
    'components.energy_goals',
    'components.makahiki_auth',
    'components.makahiki_avatar',
    'components.makahiki_badges',
    'components.makahiki_base',
    'components.makahiki_facebook',
    'components.makahiki_profiles',
    'components.makahiki_themes',
    'components.prizes',
    'components.quests',
    'components.resources',
    'components.standings',
	'components.logging',
    
    # 3rd party libraries
    'lib.brabeion',
    'lib.minidetector',
    
    # Django and Pinax apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    # 'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.messages',
    'pinax.templatetags',
    
    # external
    'notification', # must be first
    # 'django_openid',
    'emailconfirmation',
    'mailer',
    'pagination',
    'timezones',
    'ajax_validation',
    'uni_form',
    'dbtemplates',
    'staticfiles',
    'django_extensions',
    
    # internal (for now)
    # 'basic_profiles',
    'account',
    'django.contrib.admin',
    
    # project specific
    'sorl.thumbnail',
    'frontendadmin',
    'attachments',
    'django.contrib.markup',
    'django_generic_flatblocks',
    'django_generic_flatblocks.contrib.gblocks',
    
    # Dependencies for Sentry (http://justcramer.com/django-sentry/install.html)
    # Used for error tracking.
    'indexer',
    'paging',
    'sentry',
    'sentry.client',
    
    # migration support. comment out if module is not installed.
    'south',
)

FIXTURE_DIRS = [
    os.path.join(PROJECT_ROOT, "fixtures"),
]

ABSOLUTE_URL_OVERRIDES = {
    "auth.user": lambda o: "/profiles/profile/%s/" % o.username,
}

MARKUP_FILTER_FALLBACK = 'none'
MARKUP_CHOICES = (
    ('restructuredtext', u'reStructuredText'),
    ('textile', u'Textile'),
    ('markdown', u'Markdown'),
    ('creole', u'Creole'),
)
WIKI_MARKUP_CHOICES = MARKUP_CHOICES

AUTH_PROFILE_MODULE = 'makahiki_profiles.Profile'
NOTIFICATION_LANGUAGE_MODULE = 'account.Account'

# ACCOUNT_OPEN_SIGNUP is not used by this project, but it acts as if it was
# set to False
ACCOUNT_OPEN_SIGNUP = False
ACCOUNT_REQUIRED_EMAIL = False
ACCOUNT_EMAIL_VERIFICATION = False

EMAIL_CONFIRMATION_DAYS = 2
EMAIL_DEBUG = DEBUG
CONTACT_EMAIL = "feedback@example.com"
SITE_NAME = "Kukui Cup"
LOGIN_URL = "/account/cas/login/"
LOGIN_REDIRECT_URLNAME = "home_index"
LOGIN_REDIRECT_URL = "/"

SERIALIZATION_MODULES = {
    "jsonfk": "pinax.core.serializers.jsonfk",
}

# If demo flag is set, use the additional demo settings.
DEMO = False

# Load additional settings files
try:
  from makahiki_settings import *
except ImportError:
  pass
    
try:
  from competition_settings import *
except ImportError:
  pass
  
try:
  from local_settings import *
except ImportError:
  pass

try:
    INSTALLED_APPS += LOCAL_INSTALLED_APPS
except:
    pass

# Note that the following settings override the previous settings.
if DEMO:
  try:
    from demo.local_settings import *
  except ImportError:
    pass

  try:
    from demo.competition_settings import *
  except ImportError:
    pass
	
# Logging module
PROJECT_DIR = os.path.dirname(__file__)
PARENT_DIR = os.path.dirname(PROJECT_DIR)
logging.basicConfig(level=logging.DEBUG,
     format='%(asctime)s %(levelname)s %(message)s',
     filename=os.path.join(PARENT_DIR, 'django.log'),
     filemode='a+')