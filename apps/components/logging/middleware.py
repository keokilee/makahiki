import logging
import traceback
import sys
from time import strftime # Timestamp

class LoggingMiddleware(object):

	def process_response(self, request, response):
		if hasattr(request, "user") and request.user.is_authenticated():
			user = request.user
			path = request.path
		
			# Timestamp yyyy-mm-dd Time
			# timestamp = strftime("%Y-%m-%d %H:%M:%S")
	
			if request.META.has_key("HTTP_REFERER"):
				try:
					if request.GET["ref"] == "nav-button":
						logging.info(user.username + ' "' + "GET " + request.GET["ref"] + '" ' + path + " 200")
				except Exception:
					pass
		return response