import re

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

class CheckSetupMiddleware(object):
  """This middleware checks if the logged in user has completed the setup process."""
  
  def process_request(self, request):
    user = request.user
    path = request.path
    is_mobile = request.mobile
    # We need to check if the user is going to the home page so we don't get caught in a redirect loop.
    # We do need to filter out requests for CSS and other resources.
    pattern = re.compile("^/(m\/setup|account|home|site_media|media|favicon.ico)/")
    needs_setup = user.is_authenticated() and not user.get_profile().setup_complete
    if is_mobile and needs_setup and not pattern.match(path):
      return HttpResponseRedirect(reverse("mobile_setup"))
    elif needs_setup and not pattern.match(path):
      return HttpResponseRedirect(reverse("home_index"))
    return None
