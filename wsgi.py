import os
import sys
os.environ['DJANGO_SETTINGS_MODULE']  = 'makahiki.settings'
sys.path.insert(0, join(settings.PROJECT_ROOT, "apps"))
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
