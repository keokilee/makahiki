import logging
import re
import string
from time import strftime # Timestamp

from django.conf import settings

# Filter out requests to media and site_media.
media_regexp = r'^\/(site_)?media'

class LoggingMiddleware(object):
  def process_response(self, request, response):
    """
    Log the actions of logged in users.
    """
    if hasattr(request, "user") and request.user.is_authenticated():
      user = request.user
      path = request.path
      code = response.status_code
      method = request.method
      ip_addr = request.META["REMOTE_ADDR"] if request.META.has_key("REMOTE_ADDR") else "no-ip"
      # Timestamp yyyy-mm-dd Time
      timestamp = strftime("%Y-%m-%d %H:%M:%S")
    
      if not re.match(media_regexp, path) and path != "/favicon.ico":
        entry = "%s %s %s %s %s %d" % (timestamp, ip_addr, user.username, method, path, code)
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
    
    return response 