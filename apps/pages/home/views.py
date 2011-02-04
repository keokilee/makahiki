import simplejson as json

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required

import components.makahiki_facebook.facebook as facebook
from components.makahiki_facebook.models import FacebookProfile
from pages.home.forms import FacebookForm, ProfileForm

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
    if request.method == "POST":
      form = FacebookForm(request.POST)
      if form.is_valid(): # Should always be valid since nothing is required.
        fb_user = facebook.get_user_from_cookie(request.COOKIES, settings.FACEBOOK_APP_ID, settings.FACEBOOK_SECRET_KEY)
        fb_profile = FacebookProfile.create_or_update_from_fb_user(request.user, fb_user)
        fb_profile.can_post = form.cleaned_data["can_post"]
        fb_profile.save()
        
        return _get_profile_form(request)
      
    else:
      form = FacebookForm()
      response = render_to_string("home/first-login/facebook.html", {
        "form": form,
      }, context_instance=RequestContext(request))

      return HttpResponse(json.dumps({
          "title": "Introduction: Step 3 of 7",
          "contents": response,
      }), mimetype='application/json')
    
  raise Http404
  
@login_required
def setup_profile(request):
  """
  Displays the profile form.
  """
  if request.is_ajax():
    if request.method == "POST":
      pass
      
    return _get_profile_form(request)

  raise Http404
  
  
def _get_profile_form(request):
  """
  Private method to return the profile form.
  """
  form = ProfileForm(initial={
    "display_name": request.user.get_profile().name,
  })
  response = render_to_string("home/first-login/profile.html", {
    "form": form,
  }, context_instance=RequestContext(request))

  return HttpResponse(json.dumps({
      "title": "Introduction: Step 4 of 7",
      "contents": response,
  }), mimetype='application/json')