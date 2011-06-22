import logging
import re
from time import strftime # Timestamp

from django.conf import settings

class LoggingMiddleware(object):
  # Filter out requests to media and site_media.
  media_regexp = r'^\/(site_)?media'
  
  def process_response(self, request, response):
    if hasattr(request, "user") and request.user.is_authenticated():
      user = request.user
      path = request.path
      code = response.status_code

      # Timestamp yyyy-mm-dd Time
      timestamp = strftime("%Y-%m-%d %H:%M:%S")
      
      if not re.match(self.media_regexp, path):
        logger = logging.getLogger("makahiki_logger")
        logger.info(timestamp + " " + user.username + " " + path + " " + str(code))
    
    return response 