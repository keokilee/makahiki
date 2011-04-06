import sys
import logging
from time import strftime

#Middleware which activates the logging system.
class LoggingMiddleware(object):
	def process_response(self, request, response):
		user = request.user
		path = request.path
		pageStatus = response.status_code
		#Timestamp yyyy-mm-dd Time
		timestamp = strftime("%Y-%m-%d %H:%M:%S")
		#File to place the log file.
		LOG_FILENAME = 'apps/components/logging/LoggingFile/logging.log' 
		
		#Statement to see where user is going to and coming from.
		if request.META.has_key("HTTP_REFERER"):
			#Statements to see if user uses the navigational buttons at the top of the page.
			try:
				if request.GET["ref"] == "nav-button":
					logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)
					logging.info(" " + timestamp + " " + user.username + ' "' + "GET " + request.GET["ref"] + '" ' + path + " %d" % (pageStatus))
			except Exception:
				pass
		#Testing
		"""if request.get_full_path() == "/home/setup/terms/":
			logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)
			logging.info(timestamp.isoformat() + " " + user.username + " " + path + " Clicked Terms and Conditions")
		elif request.get_full_path() == "/home/setup/facebook/":
			logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)
			logging.info(timestamp.isoformat() + " " + user.username + " " + path + " Agreed to Terms and Conditions")
		elif request.get_full_path() == "/home/setup/profile/":
			logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)
			logging.info(timestamp.isoformat() + " " + user.username + " " + path + " Skipped Facebook integration")"""
		
		return response

"""
NOTES:

	EXAMPLE FOR USING META COMMAND HTTP_REFERER.
	if request.META.has_key("HTTP_REFERER"):
		logging.warn(request.META['HTTP_REFERER'])
		
"""