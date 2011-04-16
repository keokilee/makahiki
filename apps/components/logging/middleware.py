import logging
import os.path
import traceback
import sys
from time import strftime # Timestamp

class LoggingMiddleware(object):
	def process_response(self, request, response):
		LOG_FILENAME = 'apps/components/logging/LogFile/RoundONE.log' 
		logging.basicConfig(level=logging.INFO, format='%(levelname)s %(asctime)s %(message)s', 
			filename=LOG_FILENAME, 
			filemode='a+')
		if hasattr(request, "user") and request.user.is_authenticated():
			user = request.user
			path = request.path
			code = response.status_code
		
			# Timestamp yyyy-mm-dd Time
			# timestamp = strftime("%Y-%m-%d %H:%M:%S")
	
			if request.META.has_key("HTTP_REFERER"):
				try:
					if request.GET["ref"] == "nav-button":
						logging.info(user.username + ' "' + "GET " + request.GET["ref"] + '" ' + path + " " + 
						str(code))
				except Exception:
					pass
		return response