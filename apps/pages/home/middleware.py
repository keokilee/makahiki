import re

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

class CheckSetupMiddleware(object):
  """This middleware checks if the logged in user has completed the setup process."""
  
  def process_request(self, request):
    user = request.user
    path = request.path
    # We need to check if the user is going to the home page so we don't get caught in a redirect loop.
    # We do need to filter out requests for CSS and other resources.
    pattern = re.compile("^/(home|site_media|media|favicon.ico)/")
    if user.is_authenticated() and not pattern.match(path) and not user.get_profile().setup_complete:
      return HttpResponseRedirect(reverse("home_index"))
    return None
