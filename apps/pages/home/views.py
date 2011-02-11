import cgi
import json
import datetime
import urllib2

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from components.makahiki_avatar.models import avatar_file_path, Avatar

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
    return _get_profile_form(request)
    
  # Fields with file uploads are not AJAX requests.
  if request.method == "POST":
    form = ProfileForm(request.POST)
    profile = request.user.get_profile()
    
    # print request
    if form.is_valid():
      profile.name = form.cleaned_data["display_name"]
      profile.about = form.cleaned_data["about"]
      if not profile.setup_profile:
        profile.setup_profile = True
        profile.add_points(5, datetime.datetime.today())
      profile.save()
      
      if 'avatar' in request.FILES:
        path = avatar_file_path(user=request.user, 
            filename=request.FILES['avatar'].name)
        avatar = Avatar(
            user = request.user,
            primary = True,
            avatar = path,
        )
        # print "saving avatar to " + path
        new_file = avatar.avatar.storage.save(path, request.FILES['avatar'])
        avatar.save()
        
      elif form.cleaned_data["use_fb_photo"] and form.cleaned_data["facebook_photo"]:
        # Need to download the image from the url and save it.
        photo_temp = NamedTemporaryFile(delete=True)
        fb_url = form.cleaned_data["facebook_photo"]
        photo_temp.write(urllib2.urlopen(fb_url).read())
        photo_temp.flush()
        
        path = avatar_file_path(user=request.user, 
            filename="fb_photo.jpg")
        avatar = Avatar(
            user = request.user,
            primary = True,
            avatar = path,
        )
        # print "saving facebook photo to " + path
        new_file = avatar.avatar.storage.save(path, File(photo_temp))
        avatar.save()
        
      return setup_activity(request, non_xhr=True)
        
    return _get_profile_form(request, form=form, non_xhr=True)
    
  raise Http404
  
def _get_profile_form(request, form=None, non_xhr=False):
  """
  Private method to return the profile form.
  """
  if not form:
    user_info = {
      "display_name": request.user.get_profile().name,
    }
    
    # Update the form with the user's FB picture.
    try:
      user_info.update({
        "facebook_photo": "http://graph.facebook.com/%s/picture?type=large" % request.user.facebookprofile.profile_id
      })
    except FacebookProfile.DoesNotExist:
      pass
      
    form = ProfileForm(initial=user_info)
    
  response = render_to_string("home/first-login/profile.html", {
    "form": form,
  }, context_instance=RequestContext(request))

  if non_xhr:
    return HttpResponse('<textarea>' + json.dumps({
        "title": "Introduction: Step 4 of 7",
        "contents": cgi.escape(response),
    }) + '</textarea>', mimetype='text/html')
  else:
    return HttpResponse(json.dumps({
        "title": "Introduction: Step 4 of 7",
        "contents": response,
    }), mimetype='application/json')
    
@login_required
def setup_activity(request, non_xhr=False):
  if request.is_ajax():
    template = render_to_string("home/first-login/activity.html", {}, context_instance=RequestContext(request))
    
    response = HttpResponse(json.dumps({
        "title": "Introduction: Step 5 of 7",
        "contents": template,
    }), mimetype='application/json')
    
    return response
    
  elif non_xhr:
    template = render_to_string("home/first-login/activity.html", {}, context_instance=RequestContext(request))
    
    response = HttpResponse("<textarea>" + json.dumps({
        "title": "Introduction: Step 5 of 7",
        "contents": cgi.escape(template),
    }) + "</textarea>", mimetype='text/html')
    
    return response
    
  raise Http404
  
@login_required
def setup_question(request):
  if request.is_ajax():
    template = render_to_string("home/first-login/question.html", {}, context_instance=RequestContext(request))
    
    response = HttpResponse(json.dumps({
        "title": "Introduction: Step 6 of 7",
        "contents": template,
    }), mimetype='application/json')
    
    return response
  raise Http404
  
@login_required
def setup_complete(request):
  if request.is_ajax():
    profile = request.user.get_profile()
    if request.method == "POST":
      # User got the question right.
      if not profile.setup_complete:
        profile.add_points(15, datetime.datetime.today())
        
    profile.setup_complete = True
    profile.save()
    template = render_to_string("home/first-login/complete.html", {}, context_instance=RequestContext(request))

    response = HttpResponse(json.dumps({
        "title": "Introduction: Step 7 of 7",
        "contents": template,
    }), mimetype='application/json')

    return response
  raise Http404
    