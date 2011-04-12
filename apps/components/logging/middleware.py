import logging

class LoggingMiddleware(object):

	def process_request(self, request):
		logging.debug("hello world!")
		logging.info("this is some interesting info!")
		logging.error("this is an error!")
		
		return None: