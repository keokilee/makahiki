import sys
import logging
from time import strftime

#Middleware which activates the logging system.
class LoggingMiddleware(object):
	def process_request(self, request):
		user = request.user
		path = request.path
		#Timestamp yyyy-mm-dd Time
		timestamp = strftime("%Y-%m-%d %H:%M:%S")
		#File to place the log file.
		LOG_FILENAME = 'apps/components/logging/LoggingFile/logging.log' 
		
		logging.warn("WORKING")
		
		#Statement to see where user is going to and coming from.
		if request.META.has_key("HTTP_REFERER"):
			logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)
			logging.info(" " + timestamp + " " + user.username + ' "' + "GET " + path + '" ' + request.META['HTTP_REFERER'] + " 200")
			#Statements to see if user uses the navigational buttons at the top of the page.
			try:
				if request.GET["ref"] == "home-nav-button":
					logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)
					logging.info(" " + timestamp + " " + user.username + ' "' + "GET " + request.GET["ref"] + '" ' + path + " 200")
				elif request.GET["ref"] == "energy_index-nav-button":
					logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)
					logging.info(" " + timestamp + " " + user.username + ' "' + "GET " + request.GET["ref"] + '" ' + path + " 200")
				elif request.GET["ref"] == "activity_index-nav-button":
					logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)
					logging.info(" " + timestamp + " " + user.username + ' "' + "GET " + request.GET["ref"] + '" ' + path + " 200")
				elif request.GET["ref"] == "news_index-nav-button":
					logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)
					logging.info(" " + timestamp + " " + user.username + ' "' + "GET " + request.GET["ref"] + '" ' + path + " 200")
				elif request.GET["ref"] == "help_index-nav-button":
					logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)
					logging.info(" " + timestamp + " " + user.username + ' "' + "GET " + request.GET["ref"] + '" ' + path + " 200")
				elif request.GET["ref"] == "profile_index-nav-button":
					logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)
					logging.info(" " + timestamp + " " + user.username + ' "' + "GET " + request.GET["ref"] + '" ' + path + " 200")
				elif request.GET["ref"] == "prizes_index-nav-button":
					logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)
					logging.info(" " + timestamp + " " + user.username + ' "' + "GET " + request.GET["ref"] + '" ' + path + " 200")
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
		
		return None

"""
NOTES:

	EXAMPLE FOR USING META COMMAND HTTP_REFERER.
	if request.META.has_key("HTTP_REFERER"):
		logging.warn(request.META['HTTP_REFERER'])
		
"""