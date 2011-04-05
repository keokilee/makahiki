import re
import logging

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

class LoggingMiddleware(object):
	"""This middleware activates the logging system."""
	
	def process_request(self, request):
		user = request.user
		path = request.path
		
		logging.warn("hello")