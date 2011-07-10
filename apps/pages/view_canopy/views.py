from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.cache import never_cache

@never_cache
@login_required
def index(request):
  """
  Directs the user to the canopy page.
  """
  return render_to_response("canopy/index.html", {}, context_instance=RequestContext(request))
  