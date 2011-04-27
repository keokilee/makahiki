import logging
import os.path
import traceback
import sys
from time import strftime # Timestamp

class LoggingMiddleware(object):
    def process_response(self, request, response):
        LOG_FILENAME = 'apps/components/logging/LogFile/RoundONE.log' 
        
        if hasattr(request, "user") and request.user.is_authenticated():
            user = request.user
            path = request.path
            code = response.status_code
        
            # Timestamp yyyy-mm-dd Time
            timestamp = strftime("%Y-%m-%d %H:%M:%S")
    
            if request.META.has_key("HTTP_REFERER"):
                logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s', filename=LOG_FILENAME, filemode='a+')
                logging.info(timestamp + " " + user.username + " " + path + " " + str(code))
        return response	