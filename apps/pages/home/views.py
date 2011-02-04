import simplejson as json

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required

from pages.home.forms import FacebookForm

@login_required
def index(request):
  """
  Directs the user to the home page.
  """
  return render_to_response("home/index.html", {}, context_instance=RequestContext(request))

@login_required
def setup_welcome(request):
  """
  Uses AJAX to display the initial setup page.
  """
  if request.is_ajax():
    response = render_to_string("home/first-login/welcome.html", {}, context_instance=RequestContext(request))
    
    return HttpResponse(json.dumps({
        "title": "Introduction: Step 1 of 7",
        "contents": response,
    }), mimetype='application/json')
    
  raise Http404
  
@login_required
def terms(request):
  """
  Uses AJAX to display a terms and conditions page.
  """
  if request.is_ajax():
    response = render_to_string("home/first-login/terms.html", {}, context_instance=RequestContext(request))
    
    return HttpResponse(json.dumps({
        "title": "Introduction: Step 2 of 7",
        "contents": response,
    }), mimetype='application/json')
    
  raise Http404
  
@login_required
def facebook_connect(request):
  """
  Displays the Facebook connect page.
  """
  if request.is_ajax():
    form = FacebookForm()
    response = render_to_string("home/first-login/facebook.html", {
      "form": form,
    }, context_instance=RequestContext(request))
    
    return HttpResponse(json.dumps({
        "title": "Introduction: Step 3 of 7",
        "contents": response,
    }), mimetype='application/json')
    
  raise Http404