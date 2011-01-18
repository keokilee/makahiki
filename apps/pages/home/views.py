from django.shortcuts import render_to_response
from django.template import RequestContext

from django.contrib.auth.decorators import login_required

@login_required
def index(request):
  return render_to_response("home/index.html", {}, context_instance=RequestContext(request))