import logging
import re
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
      # Timestamp yyyy-mm-dd Time
      timestamp = strftime("%Y-%m-%d %H:%M:%S")
    
      if not re.match(media_regexp, path) and path != "/favicon.ico":
        entry = "%s %s %s %s %d" % (timestamp, user.username, method, path, code)
        if request.method == "POST":
          # Dump the POST parameters, but we don't need the CSRF token.
          query_dict = request.POST.copy()
          # print query_dict
          if query_dict.has_key(u"csrfmiddlewaretoken"):
            del query_dict[u'csrfmiddlewaretoken']
          
          entry += " %s" % (query_dict,)
        
        logger = logging.getLogger("makahiki_logger")
        logger.info(entry)
    
    return response 