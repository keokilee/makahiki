import os
from os.path import abspath, dirname, join
import sys

os.environ['DJANGO_SETTINGS_MODULE']  = 'makahiki.settings'
sys.path.insert(0, abspath(join(dirname(__file__), "../")))

from django.conf import settings

sys.path.insert(0, join(settings.PROJECT_ROOT, "apps"))
from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()
