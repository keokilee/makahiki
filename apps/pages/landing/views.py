from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.conf import settings
from django.views.decorators.cache import never_cache

@never_cache
def index(request):
  if request.mobile and not request.COOKIES.has_key("mobile-desktop"):
    # return HttpResponseRedirect(reverse("mobile_landing"))
    return HttpResponseRedirect(reverse("mobile_temp"))
  elif request.user.is_authenticated():
    return HttpResponseRedirect(reverse("home_index"))
  elif hasattr(settings, "ROOT_REDIRECT_URL") and settings.ROOT_REDIRECT_URL:
    return HttpResponseRedirect(settings.ROOT_REDIRECT_URL)
    
  return landing(request)
  
def landing(request):
  return render_to_response("landing/index.html", {}, context_instance=RequestContext(request))
  
def about(request):
  return render_to_response("landing/about.html", {}, context_instance=RequestContext(request))  