import datetime
import simplejson as json

from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.cache import never_cache
from django.db.models import Count, Max
from django.views.decorators.cache import never_cache
from django.contrib import messages

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

@never_cache
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
  
  notification = None
  notify = request.REQUEST.get("notify", None)
  value = request.REQUEST.get("value", None)
  if value and value != "None":
    if notify == "drop_commit":
      notification = "Commitment dropped, you lose " + value + " points."
    if notify == "drop_activity":
      notification = "Removed from signup list, you lose " + value + " points."

  # Check for the about cookie.
  hide_about = False
  if request.COOKIES.has_key("grid-hide-about"):
    hide_about = True
 
  form = EventCodeForm()
  
  return render_to_response("view_activities/index.html", {
    "events": events,
    "profile":user.get_profile(),
    "floor": floor,
    "categories":categories_list,
    "current_round": round_name or "Overall",
    "floor_standings": floor_standings,
    "profile_standings": profile_standings,
    "user_floor_standings": user_floor_standings,
    "notification":notification,
    "hide_about": hide_about,
    "event_form": form,
  }, context_instance=RequestContext(request))

## new design, return the category list with the tasks info
def __get_categories(user):
  categories = Category.objects.all() 

  for cat in categories:
    task_list = []
    for task in cat.activitybase_set.order_by("priority"):   
      task_list.append(annotate_task_status(user, task))
    
    cat.task_list = task_list
    
  return categories

@never_cache
@login_required
def view_codes(request, slug):
  """View the confirmation codes for a given activity."""
  
  if not request.user or not request.user.is_staff:
    raise Http404
    
  activity = get_object_or_404(Activity, slug=slug)
  codes = ConfirmationCode.objects.filter(activity=activity)
  if len(codes) == 0:
    raise Http404
  
  return render_to_response("view_activities/view_codes.html", {
    "activity": activity,
    "codes": codes,
  }, context_instance = RequestContext(request))
  
def attend_code(request):
  """claim the attendance code"""
  
  user = request.user
  activity_member = None
  message = None
  social_email = None
  
  if request.is_ajax() and request.method == "POST":
    form = EventCodeForm(request.POST)
    if form.is_valid():
      try:
        code = ConfirmationCode.objects.get(code=form.cleaned_data["response"])
     
        if not code.is_active:
          message = "This code has already been used."
        # Check if the user has already submitted a code for this activity.
        elif code.activity in user.activity_set.filter(activitymember__award_date__isnull=False):
          message = "You have already redemmed a code for this event/excursion."          
        elif code.activity.social_bonus:
          if form.cleaned_data["social_email"]:
            if form.cleaned_data["social_email"] != "Email":
              ref_user = get_user_by_email(form.cleaned_data["social_email"]) 
              if ref_user == None or ref_user == user:
                message = "Invalid email. Please input only one valid email."
                social_email = "true"
            else: 
              message = " "
              social_email = "true"
      except ConfirmationCode.DoesNotExist:
        message = "This code is not valid."
      except KeyError:
        message = "Please input code."
      
      print message
      
      if message:
        return HttpResponse(json.dumps({
          "message": message,
          "social_email": social_email
          }), mimetype="application/json")
            
      try:
        activity_member = ActivityMember.objects.get(user=user, activity=code.activity)
        # decrease sign up points
        user.get_profile().remove_points(2, datetime.datetime.today() - datetime.timedelta(minutes=1))
        user.get_profile().save()
      except ObjectDoesNotExist:
        activity_member = ActivityMember(user=user, activity=code.activity)
        
      activity_member.approval_status = "approved" # Model save method will award the points.
      value = code.activity.point_value  

      if form.cleaned_data.has_key("social_email") and form.cleaned_data["social_email"] != "Email":
        activity_member.user_comment = form.cleaned_data["social_email"]
        
      activity_member.save()

      code.is_active = False
      code.save()
      
      return HttpResponse(json.dumps({
        "type":code.activity.type,
        "slug":code.activity.slug,
        "notify": "add_point",
        "value":str(value)
      }), mimetype="application/json")
          
    # At this point there is a form validation error.
    return HttpResponse(json.dumps({
        "message": "Please input code."
    }), mimetype="application/json")
  
  raise Http404
            
### Private methods.
def __add_commitment(request, commitment):
  """Commit the current user to the commitment."""
  user = request.user
  floor = user.get_profile().floor
  value = None
  
  if request.method == "POST":
    form = CommitmentCommentForm(request.POST, request=request)
    if form.is_valid():  
      members = CommitmentMember.objects.filter(user=user, commitment=commitment);
      if members.count() > 0 and members[0].days_left() == 0:
        #commitment end, award full point
        member = members[0]
        member.award_date = datetime.datetime.today()
        member.comment = form.cleaned_data["social_email"]
        member.save()
        user.get_profile().remove_points(2, datetime.datetime.today() - datetime.timedelta(minutes=1))
        user.get_profile().save()
        value = commitment.point_value
    else:
       return render_to_response("view_activities/task.html", {
         "task":commitment,
         "pau":True,
         "form":form,
         "question":None,
         "member_all":0,
         "member_floor":0,
         "display_form":True,
         "form_title": "Get your points",
         }, context_instance=RequestContext(request))    
    
  if commitment not in user.commitment_set.all() and can_add_commitments(user):
    # User can commit to this commitment.
    member = CommitmentMember(user=user, commitment=commitment)
    member.save()
    # messages.info("You are now committed to \"%s\"" % commitment.title)

    #decrease the point from signup
    user.get_profile().add_points(2, datetime.datetime.today() - datetime.timedelta(minutes=1))
    user.get_profile().save()
    value = 2
    
    # Check for Facebook.
    # try:
    #   import makahiki_facebook.facebook as facebook
    #   
    #   fb_user = facebook.get_user_from_cookie(request.COOKIES, settings.FACEBOOK_APP_ID, settings.FACEBOOK_SECRET_KEY)
    #   if fb_user:
    #     try:
    #       graph = facebook.GraphAPI(fb_user["access_token"])
    #       graph.put_object("me", "feed", message="I am now committed to \"%s\" in the Kukui Cup!" % commitment.title)
    #     except facebook.GraphAPIError:
    #       # Incorrect user token.
    #       pass
    #       
    # except ImportError:
    #   # Facebook not enabled.
    #   pass
        
  return HttpResponseRedirect(reverse("activity_task", args=(commitment.type, commitment.slug,))+"?notify=add_point&value="+str(value))

def __drop_commitment(request, commitment):
  """drop the commitment."""
  user = request.user
  floor = user.get_profile().floor

  if commitment in user.commitment_set.all():
    # User can drop this commitment.
    member = user.commitmentmember_set.get(commitment=commitment)
    member.delete()

    #decrease sign up point
    user.get_profile().remove_points(2, datetime.datetime.today() - datetime.timedelta(minutes=1))
    user.get_profile().save()
    value = 2
      
    # messages.info("You are now drop commitment to \"%s\"" % commitment.title)

    return HttpResponseRedirect(reverse("activity_index", args=())+"?notify=drop_commit&value="+str(value))

def __add_activity(request, activity):
  """Commit the current user to the activity."""
  user = request.user
  floor = user.get_profile().floor
  value = None
  
  # Search for an existing activity for this user
  if activity not in user.activity_set.all():
    if activity.type == 'survey':
      question = TextPromptQuestion.objects.filter(activity=activity)
      form = SurveyForm(request.POST or None, questions=question)
    
      if form.is_valid():
        for i,q in enumerate(question):
          activity_member = ActivityMember(user=user, activity=activity)
          activity_member.question = q
          activity_member.response = form.cleaned_data['choice_response_%s' % i]
          
          if i == (len(question)-1):
            activity_member.approval_status = "approved"
            
          activity_member.save()
          value = activity.point_value
          
      else:   # form not valid
        return render_to_response("view_activities/task.html", {
            "task":activity,
            "pau":False,
            "form":form,
            "question":question,
            "display_form":True,
            "form_title": "Survey",
            }, context_instance=RequestContext(request))    
          
    else:
      activity_member = ActivityMember(user=user, activity=activity)
      activity_member.save()
        
      #increase point
      user.get_profile().add_points(2, datetime.datetime.today() - datetime.timedelta(minutes=1))
      user.get_profile().save()
      value = 2
      
    return HttpResponseRedirect(reverse("activity_task", args=(activity.type, activity.slug,))+"?notify=add_point&value="+str(value))

def __drop_activity(request, activity):
  """drop the current user from the activity."""
  user = request.user
  floor = user.get_profile().floor
  
  # Search for an existing activity for this user
  if activity in user.activity_set.all():
    activity_member = user.activitymember_set.get(activity=activity)
    activity_member.delete()
        
    #decrease point
    user.get_profile().remove_points(2, datetime.datetime.today() - datetime.timedelta(minutes=1))
    user.get_profile().save()

    return HttpResponseRedirect(reverse("activity_index", args=())+"?notify=drop_activity&value=2")

def __request_activity_points(request, activity):
  """Creates a request for points for an activity."""
  
  user = request.user
  floor = user.get_profile().floor
  question = None
  activity_member = None
  value = None
  
  try:
    # Retrieve an existing activity member object if it exists.
    activity_member = ActivityMember.objects.get(user=user, activity=activity)
      
  except ObjectDoesNotExist:
    pass # Ignore for now.

  if request.method == "POST":
    if activity.confirm_type == "image":
      form = ActivityImageForm(request.POST, request.FILES, request=request)
    elif activity.confirm_type == "free":
      form = ActivityFreeResponseForm(request.POST, request=request)
    else:
      form = ActivityTextForm(request.POST, request=request, activity=activity)
    
    ## print activity.confirm_type
    if form.is_valid():
      if not activity_member:
        activity_member = ActivityMember(user=user, activity=activity)
      
      # Attach image if it is an image form.
      if form.cleaned_data.has_key("image_response"):
        path = activity_image_file_path(user=user, filename=request.FILES['image_response'].name)
        activity_member.image = path
        new_file = activity_member.image.storage.save(path, request.FILES["image_response"])
        activity_member.approval_status = "pending"

      elif activity.confirm_type == "code":
        # Approve the activity (confirmation code is validated in forms.ActivityTextForm.clean())
        code = ConfirmationCode.objects.get(code=form.cleaned_data["response"])
        code.is_active = False
        code.save()
        activity_member.approval_status = "approved" # Model save method will award the points.
        # decrease sign up points
        user.get_profile().remove_points(2, datetime.datetime.today() - datetime.timedelta(minutes=1))
        user.get_profile().save()
        value = activity.point_value
        
      # Attach text prompt question if one is provided
      elif form.cleaned_data.has_key("question"):
        activity_member.question = TextPromptQuestion.objects.get(pk=form.cleaned_data["question"])
        activity_member.response = form.cleaned_data["response"]
        activity_member.approval_status = "pending"
                
      elif activity.confirm_type == "free":
        activity_member.response = form.cleaned_data["response"]
        activity_member.approval_status = "pending"

      activity_member.user_comment = form.cleaned_data["social_email"]
      activity_member.save()
          
      return HttpResponseRedirect(reverse("activity_task", args=(activity.type, activity.slug,))+"?notify=add_point&value="+str(value))
    
    if activity.confirm_type == "text":
      question = activity.pick_question(user.id)
      ##if question:
      ##  form = ActivityTextForm(initial={"question" : question.pk}, question_id=question.pk)
      
    return render_to_response("view_activities/task.html", {
    "task":activity,
    "pau":False,
    "form":form,
    "question":question,
    "member_all":0,
    "member_floor":0,
    "display_form":True,
    "form_title": "Get your points",
    }, context_instance=RequestContext(request))    

@never_cache
@login_required
def task(request, activity_type, slug):
  """individual task page"""
  user = request.user
  
  floor = user.get_profile().floor
  pau = False
  question = None
  form = None
  approval = None
  can_commit = None
  member_all_count = 0
  member_floor_count = 0
  
  task = get_object_or_404(ActivityBase, type=activity_type, slug=slug)

  if is_unlock(user, task) != True:
    return HttpResponseRedirect(reverse("pages.view_activities.views.index", args=()))

  
  if task.type != "commitment":
    task = task.activity

    if task.type == "survey":
      member_all = ActivityMember.objects.exclude(user=user).filter(activity=task, approval_status="approved")
      members = ActivityMember.objects.filter(user=user, activity=task, approval_status="approved")
    else:
      member_all = ActivityMember.objects.exclude(user=user).filter(activity=task)
      members = ActivityMember.objects.filter(user=user, activity=task)

    if members.count() > 0:
      pau = True
      approval = members[0]
      
    if task.type == "survey":
      question = TextPromptQuestion.objects.filter(activity=task)
      form = SurveyForm(questions=question)    
      form_title = "Survey"
    else:
      form_title = "Get your points"
    
      # Create activity request form.
      if task.confirm_type == "image":
        form = ActivityImageForm(request=request)
      elif task.confirm_type == "text":
        question = task.pick_question(user.id)
        if question:
          form = ActivityTextForm(initial={"question" : question.pk},question_id=question.pk,request=request)
      elif task.confirm_type == "free":
        form = ActivityFreeResponseForm(request=request)
      else:
        form = ActivityTextForm(initial={"code" : 1},request=request)
                
      if task.type == "event" or task.type == "excursion":
        if not pau:
          form_title = "Sign up for this "+task.type
        
  else:  ## "Commitment"
    task = task.commitment
    members = CommitmentMember.objects.filter(user=user, commitment=task);
    if members.count() > 0:
      pau = True
      approval = members[0]
      if approval.comment:
        ref_user = User.objects.get(email=approval.comment)
        ref_members = CommitmentMember.objects.filter(user=ref_user, commitment=task)
        for m in ref_members:
          if m.award_date:
            approval.social_bonus_awarded = True
    
    member_all = CommitmentMember.objects.exclude(user=user).filter(commitment=task);
    form_title = "Make this commitment"
    form = CommitmentCommentForm(request=request)
    can_commit = can_add_commitments(user)
    
  users = []
  member_all_count = member_all.count()
  for member in member_all:
    if member.user.get_profile().floor == floor:
      member_floor_count = member_floor_count + 1
      users.append(member.user)
  
  if pau:
    member_all_count = member_all_count + 1
    member_floor_count = member_floor_count +1
    users.append(user)
   
  # Load reminders
  reminders = {}
  if task.type == "event" or task.type == "excursion":
    # Store initial reminder fields.
    reminder_init = {
        "email": user.get_profile().contact_email or user.email,
        "text_number": user.get_profile().contact_text,
        "text_carrier": user.get_profile().contact_carrier,
    }
    # Retrieve an existing reminder and update it accordingly.
    try:
      email = user.emailreminder_set.get(activity=task)
      reminders.update({"email": email})
      reminder_init.update({
          "email": email.email_address, 
          "send_email": True,
          "email_advance": str((task.activity.event_date - email.send_at).seconds / 3600)
      })
    except ObjectDoesNotExist:
      pass
    
    try:
      text = user.textreminder_set.get(activity=task)
      reminders.update({"text": text})
      reminder_init.update({
          "text_number": text.text_number, 
          "text_carrier": text.text_carrier,
          "send_text": True,
          "text_advance": str((task.activity.event_date - text.send_at).seconds / 3600)
      })
    except ObjectDoesNotExist:
      pass
      
    reminders.update({"form": ReminderForm(initial=reminder_init)})
    
  display_form = True if request.GET.has_key("display_form") else False

  notification = None
  notify = request.REQUEST.get("notify", None)
  value = request.REQUEST.get("value", None)
  if value and value != "None":
    if notify == "add_point":
      notification = "You just earned " + value + " points."
  
  return render_to_response("view_activities/task.html", {
    "task":task,
    "pau":pau,
    "approval":approval,
    "form":form,
    "question":question,
    "member_all":member_all_count,
    "member_floor":member_floor_count,
    "users":users,
    "display_form":display_form,
    "form_title": form_title,
    "can_commit":can_commit,
    "notification":notification,
    "reminders": reminders,
  }, context_instance=RequestContext(request))    

@never_cache
@login_required
def add_task(request, activity_type, slug):
  task = get_object_or_404(ActivityBase, type=activity_type, slug=slug)
  
  if task.type == "commitment":
    return __add_commitment(request, task.commitment)
    
  if task.type == "activity":
    return __request_activity_points(request, task.activity)
  elif task.type == "survey":
    return __add_activity(request, task)
  else:       ## event or excursion
    task = task.activity
    if task.is_event_completed():
      return __request_activity_points(request, task)
    else:  
      return __add_activity(request, task)
      
@login_required
def reminder(request, activity_type, slug):
  if request.is_ajax():
    if request.method == "POST":
      profile = request.user.get_profile()
      task = get_object_or_404(ActivityBase, type=activity_type, slug=slug)
      form = ReminderForm(request.POST)
      if form.is_valid():
        email_reminder = None
        text_reminder = None
        
        # Try and retrieve the reminders.
        try:
          email_reminder = EmailReminder.objects.get(user=request.user, activity=task)
          if form.cleaned_data["send_email"]:
            email_reminder.email_address = form.cleaned_data["email"]
            email_reminder.send_at = task.activity.event_date - datetime.timedelta(
                hours=int(form.cleaned_data["email_advance"])
            )
            email_reminder.save()
            
            profile.contact_email = form.cleaned_data["email"]
            profile.save()
          else:
            # If send_email is false, the user does not want the reminder anymore.
            email_reminder.delete()
            
        except EmailReminder.DoesNotExist:
          # Create a email reminder
          if form.cleaned_data["send_email"]:
            email_reminder = EmailReminder.objects.create(
                user=request.user,
                activity=task,
                email_address=form.cleaned_data["email"],
                send_at=task.activity.event_date - datetime.timedelta(
                    hours=int(form.cleaned_data["email_advance"])
                )
            )
            
            profile.contact_email = form.cleaned_data["email"]
            profile.save()
          
        try:
          text_reminder = TextReminder.objects.get(user=request.user, activity=task)
          if form.cleaned_data["send_text"]:
            text_reminder.text_number = form.cleaned_data["text_number"]
            text_reminder.text_carrier = form.cleaned_data["text_carrier"]
            text_reminder.send_at = task.activity.event_date - datetime.timedelta(
                hours=int(form.cleaned_data["text_advance"])
            )
            text_reminder.save()
            
            profile.contact_text = form.cleaned_data["text_number"]
            profile.contact_carrier = form.cleaned_data["text_carrier"]
            profile.save()
            
          else:
            text_reminder.delete()
            
        except TextReminder.DoesNotExist:
          if form.cleaned_data["send_text"]:
            text_reminder = TextReminder.objects.create(
                user=request.user,
                activity=task,
                text_number=form.cleaned_data["text_number"],
                text_carrier=form.cleaned_data["text_carrier"],
                send_at=task.activity.event_date - datetime.timedelta(
                    hours=int(form.cleaned_data["text_advance"])
                ),
            )
            
            profile.contact_text = form.cleaned_data["text_number"]
            profile.contact_carrier = form.cleaned_data["text_carrier"]
            profile.save()
          
        return HttpResponse(json.dumps({"success": True}), mimetype="application/json")
        
      template = render_to_string("view_activities/reminder_form.html", {
          "reminders": {"form": form},
          "task": task,
      })
      
      return HttpResponse(json.dumps({
          "success": False,
          "form": template,
      }), mimetype="application/json")
  
  raise Http404
    
@never_cache
@login_required
def drop_task(request, activity_type, slug):
  
  task = get_object_or_404(ActivityBase, type=activity_type, slug=slug)
  
  if task.type == "commitment":
    return __drop_commitment(request, task.commitment)
    
  if task.type == "event" or task.type == "excursion":
    return __drop_activity(request, task.activity)
   
  
