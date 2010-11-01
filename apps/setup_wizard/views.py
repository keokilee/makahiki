from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import logout
from django.http import HttpResponseRedirect

def terms(request):
  """Display the terms and conditions."""
  return render_to_response("setup_wizard/terms.html", {}, context_instance=RequestContext(request))
  
def logout(request):
  """Logs out the user if they cancel at any point."""
  logout(request)
  return HttpResponseRedirect("/")