import logging
import re
import string
from time import strftime # Timestamp

from django.conf import settings

# Filter out requests to media and site_media.
media_regexp = r'^\/(site_)?media'
sentry_regexp = r'^\/sentry\/'
url_filter = ("/favicon.ico", "/admin/jsi18n/",)

class LoggingMiddleware(object):
  def process_response(self, request, response):
    """
    Log the actions of logged in users.
    """
    # Filter out the following paths.  Logs will not be created for these paths.
    if re.match(media_regexp, request.path) or re.match(sentry_regexp, request.path) or request.path in url_filter:
      return response
    
    # Retrieve the username either from a cookie (when logging out) or the authenticated user.
    username = None
    if hasattr(request, "session") and request.session.has_key("logged-out-user"):
      username = request.session["logged-out-user"]
      del request.session["logged-out-user"]
    elif hasattr(request, "user") and request.user.is_authenticated():
      username = request.user.username
      
    if username:
      # if request.session.get('staff', False):
      #   username = username + '*'
      self.__write_log_entry(username, request, response=response)
    
    return response 
    
  # def process_exception(self, request, exception):
  #   """
  #   Process exceptions for logged in users.
  #   """
  #   # Filter out the following paths.  Logs will not be created for these paths.
  #   if re.match(media_regexp, request.path) or re.match(sentry_regexp, request.path) or request.path in url_filter:
  #     return None
  #   
  #   # Retrieve the username either from a cookie (when logging out) or the authenticated user.
  #   username = None
  #   if hasattr(request, "session") and request.session.has_key("logged-out-user"):
  #     username = request.session["logged-out-user"]
  #     del request.session["logged-out-user"]
  #   elif hasattr(request, "user") and request.user.is_authenticated():
  #     username = request.user.username
  #     
  #   if username:
  #     self.__write_log_entry(username, request, exception=exception)
  #     
  #   return None
    
  def __write_log_entry(self, username, request, response=None, exception=None):
    path = request.get_full_path()
    code = response.status_code if response else 500
    method = request.method
    ip_addr = request.META["REMOTE_ADDR"] if request.META.has_key("REMOTE_ADDR") else "no-ip"
    # Timestamp yyyy-mm-dd Time
    timestamp = strftime("%Y-%m-%d %H:%M:%S")
    
    # Create the log entry.
    entry = "%s %s %s %s %s %d" % (timestamp, ip_addr, username, method, path, code)
    if request.method == "POST":
      # Dump the POST parameters, but we don't need the CSRF token.
      query_dict = request.POST.copy()
      # print query_dict
      if query_dict.has_key(u"csrfmiddlewaretoken"):
        del query_dict[u'csrfmiddlewaretoken']
      if query_dict.has_key(u"password"):
        del query_dict[u'password']
        
      entry += " %s" % (query_dict,)
      
    if request.FILES:
      # Append the filenames to the log.
      filenames = (f.name for f in request.FILES.values())
      file_str = "<Files: %s>" % string.join(filenames, " ")
      entry += " %s" % (file_str,)
    
    logger = logging.getLogger("makahiki_logger")
    logger.info(entry)