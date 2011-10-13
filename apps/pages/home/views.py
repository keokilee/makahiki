import cgi
import json
import datetime
import urllib2

from django.shortcuts import get_object_or_404
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.db import IntegrityError

from components.activities.models import Activity, ActivityMember
from components.makahiki_avatar.models import avatar_file_path, Avatar
import components.makahiki_facebook.facebook as facebook
from pages.home.forms import FacebookForm, ProfileForm
from components.help_topics.models import HelpTopic

@never_cache
@login_required
def index(request):
  """
  Directs the user to the home page.
  """
  return render_to_response("home/index.html", {}, context_instance=RequestContext(request))
  
@login_required
def restricted(request):
  today = datetime.datetime.today()
  start = datetime.datetime.strptime(settings.COMPETITION_START, "%Y-%m-%d")
  end = datetime.datetime.strptime(settings.COMPETITION_END, "%Y-%m-%d")
  
  before = False
  if today < start:
    before = True
    
  return render_to_response("home/restricted.html", {
      "before": before,
      "start": start,
      "end": end,
  }, context_instance=RequestContext(request))

@never_cache
@login_required
def setup_welcome(request):
  """
  Uses AJAX to display the initial setup page.
  """
  if request.is_ajax():
    response = render_to_string("home/first-login/welcome.html", {}, context_instance=RequestContext(request))
    
    return HttpResponse(json.dumps({
        "title": "Introduction: Step 1 of 6",
        "contents": response,
    }), mimetype='application/json')
    
  raise Http404
  
@never_cache
@login_required
def terms(request):
  """
  Uses AJAX to display a terms and conditions page.
  """
  if request.is_ajax():
    response = render_to_string("home/first-login/terms.html", {
        'is_mobile': request.mobile,
    }, context_instance=RequestContext(request))
    
    return HttpResponse(json.dumps({
        "title": "Introduction: Step 2 of 6",
        "contents": response,
    }), mimetype='application/json')
    
  raise Http404
  
@never_cache
@login_required
def profile_facebook(request):
  """
  Connect to Facebook to get the user's facebook photo..
  """
  if request.is_ajax():
    fb_user = facebook.get_user_from_cookie(request.COOKIES, settings.FACEBOOK_APP_ID, settings.FACEBOOK_SECRET_KEY)
    fb_id = None
    if not fb_user:
      return HttpResponse(json.dumps({
          "error": "We could not access your info.  Please log in again."
      }), mimetype="application/json")
      
    try:
      graph = facebook.GraphAPI(fb_user["access_token"])
      graph_profile = graph.get_object("me")
      fb_id = graph_profile["id"]
    except facebook.GraphAPIError:
      return HttpResponse(json.dumps({
          "contents": "Facebook is not available at the moment, please try later",
      }), mimetype='application/json')
      
    # Insert the form into the response.
    user_info = {
      "facebook_photo": "http://graph.facebook.com/%s/picture?type=large" % fb_id
    }
    form = ProfileForm(initial=user_info)
    
    response = render_to_string("home/first-login/profile-facebook.html", {
      "fb_id": fb_id,
      "form": form,
    }, context_instance=RequestContext(request))
    
    return HttpResponse(json.dumps({
        "contents": response,
    }), mimetype='application/json')
      
  raise Http404
  
@never_cache
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
      profile.name = form.cleaned_data["display_name"].strip()
      if not profile.setup_profile:
        profile.setup_profile = True
        profile.add_points(5, datetime.datetime.today(), "Set up profile")
      try:
        profile.save()
      except IntegrityError:
        form.errors.update({"display_name": "'%s' is taken, please enter another name." % profile.name})
        return _get_profile_form(request, form=form, non_xhr=True)
      
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
        # print fb_url
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
        
      return HttpResponseRedirect(reverse("setup_activity"))
        
    return _get_profile_form(request, form=form, non_xhr=True)
    
  raise Http404
  
@never_cache
def _get_profile_form(request, form=None, non_xhr=False):
  """
  Helper method to render the profile form.
  """
  if not form:
    form = ProfileForm(initial={
      "display_name": request.user.get_profile().name,
    })
    
  response = render_to_string("home/first-login/profile.html", {
    "form": form,
  }, context_instance=RequestContext(request))

  if non_xhr:
    return HttpResponse('<textarea>' + json.dumps({
        "title": "Introduction: Step 3 of 6",
        "contents": cgi.escape(response),
    }) + '</textarea>', mimetype='text/html')
  else:
    return HttpResponse(json.dumps({
        "title": "Introduction: Step 3 of 6",
        "contents": response,
    }), mimetype='application/json')
    
@never_cache
@login_required
def setup_activity(request):
  if request.is_ajax():
    template = render_to_string("home/first-login/activity.html", {}, context_instance=RequestContext(request))
    
    response = HttpResponse(json.dumps({
        "title": "Introduction: Step 4 of 6",
        "contents": template,
    }), mimetype='application/json')
    
    return response
    
  else:
    template = render_to_string("home/first-login/activity.html", {}, context_instance=RequestContext(request))
    
    response = HttpResponse("<textarea>" + json.dumps({
        "title": "Introduction: Step 4 of 6",
        "contents": cgi.escape(template),
    }) + "</textarea>", mimetype='text/html')
    
    return response

@never_cache 
@login_required
def setup_question(request):
  if request.is_ajax():
    template = render_to_string("home/first-login/question.html", {}, context_instance=RequestContext(request))
    
    response = HttpResponse(json.dumps({
        "title": "Introduction: Step 5 of 6",
        "contents": template,
    }), mimetype='application/json')
    
    return response
  raise Http404

@never_cache 
@login_required
@csrf_exempt
def setup_complete(request):
  if request.is_ajax():
    profile = request.user.get_profile()
    if request.method == "POST":
      # User got the question right.
      # Originally, we added the points directly, but now we're going to link it to an activity.
      activity_name = settings.SETUP_WIZARD_ACTIVITY_NAME
      try:
        activity = Activity.objects.get(name=activity_name)
        ActivityMember.objects.get_or_create(activity=activity, user=profile.user, approval_status="approved")
        # If this was created, it's automatically saved.
      except Activity.DoesNotExist:
        # profile.add_points(15, datetime.datetime.today(), "First login activity")
        pass # Don't add anything if we can't link to the activity.
        
    profile.setup_complete = True
    profile.completion_date = datetime.datetime.today()
    profile.save()
    template = render_to_string("home/first-login/complete.html", {}, context_instance=RequestContext(request))

    response = HttpResponse(json.dumps({
        "title": "Introduction: Step 6 of 6",
        "contents": template,
    }), mimetype='application/json')

    return response
  raise Http404
    
@never_cache 
@login_required
def mobile_tc(request):
  topic = get_object_or_404(HelpTopic, slug='terms-and-conditions', category='rules')
  if request.is_ajax():
    contents = render_to_string("help/dialog.html", {"topic": topic})
    return HttpResponse(json.dumps({
        "title": topic.title,
        "contents": contents,
    }), mimetype="application/json")
  return render_to_response("home/first-login/mobile_TC.html", {
      "topic": topic,
      }, context_instance=RequestContext(request))
 

