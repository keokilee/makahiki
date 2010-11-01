import re

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

class CheckSetupMiddleware(object):
  """This middleware checks if the logged in user has completed the setup process."""
  
  def process_request(self, request):
    user = request.user
    path = request.path
    # We need to check if the user is going to setup so we don't get caught in a redirect loop.
    # The page also needs to load it's resources.
    pattern = re.compile("^/(setup|site_media|media)/")
    if user.is_authenticated() and not pattern.match(path) and not user.get_profile().setup_complete:
      # user.message_set.create(message="%s did not complete the setup." % user.username)
      return HttpResponseRedirect(reverse("setup_terms"))
    return None