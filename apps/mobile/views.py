from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext

# Create your views here.

def index(request):
  """Method that redirects the user to their profile if they are logged in."""
  if request.user.is_authenticated() and request.user.get_profile().floor:
    return HttpResponseRedirect(reverse("mobile.views.profile"))
  else:
    return login(request)
  
def login(request):
  """Provides a login link."""
  
  return render_to_response("mobile/login.html", {} context_instance=RequestContext(request))
def profile(request):
  """The home page for logged in users."""
  if not request.user.is_authenticated():
    return HttpResponseRedirect(reverse("mobile.views.login"))
    
  return render_to_response("mobile/profile.html", {} context_instance=RequestContext(request))