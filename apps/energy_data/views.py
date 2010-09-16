from django.shortcuts import render_to_response
from django.template import RequestContext
# Create your views here.

def index(request):
  """Provides a list of dorms and floors."""
  return render_to_response("energy_data/index.html", {
    
  }, context_instance = RequestContext(request))