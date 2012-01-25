import os
import sys

# redirect sys.stdout to sys.stderr for bad libraries like geopy that uses
# print statements for optional import exceptions.
sys.stdout = sys.stderr

from os.path import abspath, dirname, join
from site import addsitedir

addsitedir('/usr/local/lib/python2.7/site-packages/')

sys.path.insert(0, abspath(join(dirname(__file__), "../../")))
sys.path.insert(0, abspath(join(dirname(__file__), "../")))

from django.conf import settings
os.environ["DJANGO_SETTINGS_MODULE"] = "makahiki.settings"

sys.path.insert(0, join(settings.PROJECT_ROOT, "apps"))
#print sys.path

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
import time
import signal
import threading
import atexit
import Queue
import traceback 

FILE = '/tmp/dump-stack-traces.txt'

_interval = 1.0

_running = False
_queue = Queue.Queue()
_lock = threading.Lock()

def _stacktraces(): 
    code = [] 
    for threadId, stack in sys._current_frames().items(): 
        code.append("\n# ProcessId: %s" % os.getpid()) 
        code.append("# ThreadID: %s" % threadId) 
        for filename, lineno, name, line in traceback.extract_stack(stack): 
            code.append('File: "%s", line %d, in %s' % (filename, 
                    lineno, name)) 
            if line: 
                code.append("  %s" % (line.strip())) 

    for line in code:
        print >> sys.stderr, line

try:
    mtime = os.path.getmtime(FILE)
except:
    mtime = None

def _monitor():
    while 1:
        global mtime

        try:
            current = os.path.getmtime(FILE)
        except:
            current = None

        if current != mtime:
            mtime = current
            _stacktraces()

        # Go to sleep for specified interval.

        try:
            return _queue.get(timeout=_interval)
        except:
            pass

_thread = threading.Thread(target=_monitor)
_thread.setDaemon(True)

def _exiting():
    try:
        _queue.put(True)
    except:
        pass
    _thread.join()

atexit.register(_exiting)

def _start(interval=1.0):
    global _interval
    if interval < _interval:
        _interval = interval

    global _running
    _lock.acquire()
    if not _running:
        prefix = 'monitor (pid=%d):' % os.getpid()
        print >> sys.stderr, '%s Starting stack trace monitor.' % prefix
        _running = True
        _thread.start()
    _lock.release()

_start()