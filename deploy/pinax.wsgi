import os
import sys

# redirect sys.stdout to sys.stderr for bad libraries like geopy that uses
# print statements for optional import exceptions.
sys.stdout = sys.stderr

from os.path import abspath, dirname, join
from site import addsitedir

sys.path.insert(0, abspath(join(dirname(__file__), "../../")))

from django.conf import settings
os.environ["DJANGO_SETTINGS_MODULE"] = "kukui-cup-pinax.settings"

sys.path.insert(0, join(settings.PINAX_ROOT, "apps"))
sys.path.insert(0, join(settings.PROJECT_ROOT, "apps"))
# print sys.path

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()

# uncomment below to do a sanity check on the wsgi setup

# def test_wsgi(environ, start_response):
#     status = '200 OK'
#     output = 'Hello World! wsgi py \n' + sys.version + '\n' + '\n'.join(sys.path)
# 
#     response_headers = [('Content-type', 'text/plain'),
#                         ('Content-Length', str(len(output)))]
#     start_response(status, response_headers)
# 
#     return [output]
# 
# application = test_wsgi
