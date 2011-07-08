from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.conf import settings

def index(request):
  if request.mobile:
    return HttpResponseRedirect(reverse("mobile_landing"))
  if request.user.is_authenticated():
    return HttpResponseRedirect(reverse("home_index"))
  if hasattr(settings, "REDIRECT_TO_ABOUT") and settings.REDIRECT_TO_ABOUT:
        return HttpResponseRedirect(reverse("about"))
    
  return landing(request)
  
def landing(request):
  return render_to_response("landing/index.html", {}, context_instance=RequestContext(request))
  
def about(request):
  return render_to_response("landing/about.html", {}, context_instance=RequestContext(request))  