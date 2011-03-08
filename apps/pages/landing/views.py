from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse

def index(request):
  if request.user.is_authenticated():
    return HttpResponseRedirect(reverse("home_index"))
    
  return render_to_response("landing/index.html", {}, context_instance=RequestContext(request))