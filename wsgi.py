import os
os.environ['DJANGO_SETTINGS_MODULE']  = 'makahiki.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

