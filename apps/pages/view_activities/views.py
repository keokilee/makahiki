import datetime
import simplejson as json

from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.cache import never_cache
from django.db.models import Count, Max
from django.views.decorators.cache import never_cache

from components.makahiki_base import get_current_round
from pages.view_activities.forms import *
from components.activities.models import *
from components.activities import *
from components.floors.models import *
from components.floors import *
from components.makahiki_profiles.models import *
from components.makahiki_profiles import *

MAX_INDIVIDUAL_STANDINGS = 10
ACTIVITIES_COL_COUNT = 3

@login_required
def index(request):
  user = request.user
  events = get_available_events(user)
  floor = user.get_profile().floor
  
  current_round = get_current_round()
  round_name = current_round if current_round else None
  floor_standings = Floor.floor_points_leaders(num_results=10, round_name=round_name)
  profile_standings = Profile.points_leaders(num_results=10, round_name=round_name).select_related("scoreboardentry")
  user_floor_standings = floor.points_leaders(num_results=10, round_name=round_name).select_related("scoreboardentry")
  
  categories_list = __get_categories(user)
  
  # helps = ["Upcoming Events", "Points Score Board", "The Smart Grid Game"]
  # helpfiles = ["view_activities/help1.html", "view_activities/help2.html", "view_activities/help3.html"]
        
  return render_to_response("view_activities/index.html", {
    "events": events,
    "profile":user.get_profile(),
    "floor": floor,
    "categories":categories_list,
    "current_round": round_name or "Overall",
    "floor_standings": floor_standings,
    "profile_standings": profile_standings,
    "user_floor_standings": user_floor_standings,
    "help_info": {
      "prefix": "activities_index",
      "count": range(0, 3),
    }
  }, context_instance=RequestContext(request))

## new design, return the category list with the tasks info
def __get_categories(user):
  categories = Category.objects.all() 

  for cat in categories:
    task_list = []
    for task in cat.activitybase_set.order_by("priority"):   
      task.is_unlock = is_unlock(user, task)
      task.is_pau = is_pau(user, task)
      task_list.append(task)
    
    cat.task_list = task_list
    
  return categories
  
@login_required
def view_codes(request, activity_id):
  """View the confirmation codes for a given activity."""
  
  if not request.user or not request.user.is_staff:
    raise Http404
    
  activity = get_object_or_404(Activity, pk=activity_id)
  codes = ConfirmationCode.objects.filter(activity=activity)
  if len(codes) == 0:
    raise Http404
  
  return render_to_response("view_activities/view_codes.html", {
    "activity": activity,
    "codes": codes,
  }, context_instance = RequestContext(request))

### Private methods.

def __add_commitment(request, commitment_id):
  """Commit the current user to the commitment."""
  
  commitment = get_object_or_404(Commitment, pk=commitment_id)
  user = request.user
  floor = user.get_profile().floor
  
  if not can_add_commitments(user):
    message = "You can only have %d active commitments." % MAX_COMMITMENTS
    user.message_set.create(message=message)
  elif commitment in get_current_commitments(user):
    user.message_set.create(message="You are already committed to this commitment.")
  else:
    # User can commit to this commitment.
    member = CommitmentMember(user=user, commitment=commitment)
    member.save()
    user.message_set.create(message="You are now committed to \"%s\"" % commitment.title)

    #increase point
    user.get_profile().add_points(2, datetime.datetime.today() - datetime.timedelta(minutes=1))
    user.get_profile().save()
    
    # Check for Facebook.
    try:
      import makahiki_facebook.facebook as facebook
      
      fb_user = facebook.get_user_from_cookie(request.COOKIES, settings.FACEBOOK_APP_ID, settings.FACEBOOK_SECRET_KEY)
      if fb_user:
        try:
          graph = facebook.GraphAPI(fb_user["access_token"])
          graph.put_object("me", "feed", message="I am now committed to \"%s\" in the Kukui Cup!" % commitment.title)
        except facebook.GraphAPIError:
          # Incorrect user token.
          pass
          
    except ImportError:
      # Facebook not enabled.
      pass
      
  # Redirect back to the referrer or go to the profile if not available.
  ## next = request.META.get("HTTP_REFERER", reverse("makahiki_profiles.views.profile", args=(request.user.id,)))
  ## next = reverse("pages.view_activities.views.task", args=(commitment_id))
  ## return HttpResponseRedirect(next)
  member_all = CommitmentMember.objects.filter(commitment=commitment);

  users = []
  member_all_count = 0
  member_floor_count = 0
  member_all_count = member_all.count()
  for member in member_all:
    if member.user.get_profile().floor == floor:
      member_floor_count = member_floor_count + 1
      users.append(member.user)
  
  return render_to_response("view_activities/task.html", {
    "task":commitment,
    "type":"commitment",
    "pau":True,
    "approved":False,
    "form":None,
    "question":None,
    "member_all":member_all_count,
    "member_floor":member_floor_count,
    "users":users,
    "display_point":True,
    "display_form":False,
    "form_title": None,
  }, context_instance=RequestContext(request))    

def __add_activity(request, activity_id):
  """Commit the current user to the activity."""

  activity = get_object_or_404(Activity, pk=activity_id)
  user = request.user
  floor = user.get_profile().floor

  # Search for an existing activity for this user
  if activity not in user.activity_set.all():
    activity_member = ActivityMember(user=user, activity=activity)
    activity_member.save()
    
    #increase point
    user.get_profile().add_points(2, datetime.datetime.today() - datetime.timedelta(minutes=1))
    user.get_profile().save()
    
    user.message_set.create(message="You are now participating in the activity \"" + activity.title + "\"")
  else:
    return Http404

  # Redirect back to the referrer or go to the profile if not available.
  ## next = request.META.get("HTTP_REFERER", reverse("makahiki_profiles.views.profile", args=(request.user.id,)))
  ## next = reverse("pages.view_activities.views.task", args=(activity_id))
  ## return HttpResponseRedirect(next)
  member_all = ActivityMember.objects.filter(activity=activity);

  users = []
  member_all_count = 0
  member_floor_count = 0
  member_all_count = member_all.count()
  for member in member_all:
    if member.user.get_profile().floor == floor:
      member_floor_count = member_floor_count + 1
      users.append(member.user)
  
  return render_to_response("view_activities/task.html", {
    "task":activity,
    "type":"event",
    "pau":True,
    "approved":False,
    "form":None,
    "question":None,
    "member_all":member_all_count,
    "member_floor":member_floor_count,
    "users":users,
    "display_point":True,
    "display_form":False,
    "form_title": None,
  }, context_instance=RequestContext(request))    
  
def __request_activity_points(request, activity_id):
  """Creates a request for points for an activity."""
  
  activity = get_object_or_404(Activity, pk=activity_id)
  user = request.user
  question = None
  activity_member = None
  
  try:
    # Retrieve an existing activity member object if it exists.
    activity_member = ActivityMember.objects.get(user=user, activity=activity)
    if activity_member.award_date:
      user.message_set.create(message="You have already received the points for this activity.")
      return HttpResponseRedirect(reverse("makahiki_profiles.views.profile", args=(request.user.id,)))
      
  except ObjectDoesNotExist:
    pass # Ignore for now.

  if request.method == "POST":
    if activity.confirm_type == "image":
      form = ActivityImageForm(request.POST, request.FILES)
    elif activity.confirm_type == "free":
      form = ActivityFreeResponseForm(request.POST)
    else:
      form = ActivityTextForm(request.POST)
    
    ## print activity.confirm_type
    if form.is_valid():
      ## print 'valid'
      if not activity_member:
        activity_member = ActivityMember(user=user, activity=activity)
      
      activity_member.user_comment = form.cleaned_data["comment"]
      # Attach image if it is an image form.
      if form.cleaned_data.has_key("image_response"):
        path = activity_image_file_path(user=user, filename=request.FILES['image_response'].name)
        activity_member.image = path
        
        new_file = activity_member.image.storage.save(path, request.FILES["image_response"])
        
        activity_member.approval_status = "pending"
        user.message_set.create(message="Your request has been submitted!")

      elif activity.confirm_type == "code":
        # Approve the activity (confirmation code is validated in forms.ActivityTextForm.clean())
        code = ConfirmationCode.objects.get(code=form.cleaned_data["response"])
        code.is_active = False
        code.save()
        activity_member.approval_status = "approved" # Model save method will award the points.
        points = activity_member.activity.point_value
        message = "You have been awarded %d points for your participation!" % points
        user.message_set.create(message=message)
        
      # Attach text prompt question if one is provided
      elif form.cleaned_data.has_key("question"):
        activity_member.question = TextPromptQuestion.objects.get(pk=form.cleaned_data["question"])
        activity_member.response = form.cleaned_data["response"]
        activity_member.approval_status = "pending"
        user.message_set.create(message="Your request has been submitted!")
                
      elif activity.confirm_type == "free":
        activity_member.response = form.cleaned_data["response"]
        activity_member.approval_status = "pending"
        user.message_set.create(message="Your request has been submitted!")

      activity_member.save()
      next = reverse("pages.view_activities.views.task", args=(activity_id,))
      return HttpResponseRedirect(next)
  
    if activity.confirm_type == "text":
      question = activity.pick_question()
      if question:
        form = ActivityTextForm(initial={"question" : question.pk}, question_id=question.pk)
                  		  
    return render_to_response("view_activities/task.html", {
    "task":activity,
    "type":"Activity",
    "pau":False,
    "form":form,
    "question":question,
    "member_all":0,
    "member_floor":0,
    "display_form":True,
    "display_point":False,
    }, context_instance=RequestContext(request))    

@never_cache
def task(request, task_id):
  """individual task page"""
  user = request.user
  floor = user.get_profile().floor
  question = None
  form = None
  approved = None
  member_all_count = 0
  member_floor_count = 0
  
  task = ActivityBase.objects.get(id=task_id)
  type = task.type
  
  if task.type != "commitment":
    task = task.activity
    pau = ActivityMember.objects.filter(user=user, activity=task).count() > 0
    approved = ActivityMember.objects.filter(user=user, activity=task, approval_status='approved').count() > 0
    member_all = ActivityMember.objects.filter(activity=task);
    form_title = "Get your points"
    
    # Create activity request form.
    if task.confirm_type == "image":
      form = ActivityImageForm()
    elif task.confirm_type == "text":
      question = task.pick_question()
      if question:
        form = ActivityTextForm(initial={"question" : question.pk},question_id=question.pk)
    elif task.confirm_type == "free":
      form = ActivityFreeResponseForm()
    else:
      form = ActivityTextForm(initial={"code" : 1})
                
    if task.type == "event" or task.type == "excursion":
      type="event"   
      if not pau:
        form_title = "Sign up for this event"
        
  else:  ## "Commitment"
    task = task.commitment
    pau = CommitmentMember.objects.filter(user=user, commitment=task).count() > 0
    member_all = CommitmentMember.objects.filter(commitment=task);
    form_title = "Make this commitment"
    form = CommitmentCommentForm()

  users = []
  member_all_count = member_all.count()
  for member in member_all:
    if member.user.get_profile().floor == floor:
      member_floor_count = member_floor_count + 1
      ## print "user="+ member.user.get_profile().name
      users.append(member.user)
  
  return render_to_response("view_activities/task.html", {
    "task":task,
    "type":type,
    "pau":pau,
    "approved":approved,
    "form":form,
    "question":question,
    "member_all":member_all_count,
    "member_floor":member_floor_count,
    "users":users,
    "display_point":False,
    "display_form":False,
    "form_title": form_title,
  }, context_instance=RequestContext(request))    
    
def add_task(request, task_id):
  
  task = ActivityBase.objects.get(id=task_id)
  
  if task.type == "commitment":
    return __add_commitment(request, task_id)
  elif task.type == "event" or task.type == "excursion":
    return __add_activity(request, task_id)
  else:
    return __request_activity_points(request, task_id)
   
  
