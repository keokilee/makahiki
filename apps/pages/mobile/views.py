
import simplejson as json
from django.shortcuts import render_to_response, get_object_or_404 
from django.template import RequestContext
from django.http import Http404, HttpResponseRedirect, HttpResponse,get_host
import unicodedata
from components.activities.models import ActivityBase
from components.makahiki_base import get_current_round
from pages.view_activities.forms import *
from pages.view_help.forms import AskAdminForm
from pages.view_profile.forms import ProfileForm
from pages.view_profile import get_completed_members, get_in_progress_members
from components.makahiki_facebook.models import FacebookProfile
from components.activities.models import *
from components.activities import *  
from components.makahiki_notifications.models import UserNotification
from components.makahiki_profiles.models import *
from components.makahiki_profiles import *
from datetime import timedelta, date
from time import strftime
from django.template.defaultfilters import slugify
from string import lower
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from components.quests.models import *
from components.quests import *
from django.contrib.auth import REDIRECT_FIELD_NAME
from urlparse import urljoin
from urllib import urlencode

from pages.view_activities.views import __get_categories

from components.help_topics.models import HelpTopic

from pages.view_prizes.views import _get_prizes
from pages.view_prizes.views import _get_raffle_prizes

 
def temp(request):
  return render_to_response("mobile/temp.html", {}, context_instance=RequestContext(request))

@login_required
@never_cache
def index(request):
  return render_to_response("mobile/index.html", {}, context_instance=RequestContext(request))

@login_required
def logout(request):
  return render_to_response("mobile/logout.html", {}, context_instance=RequestContext(request))

@never_cache
@login_required
def scoreboard(request,page):
   
  page = string.lower(page)
  if( page == "index"):
    page = "overall_lounge"
  user = request.user
  events = get_available_events(user)
  floor = user.get_profile().floor
  
  current_round = get_current_round()
  round_name = current_round if current_round else None
  floor_standings = Floor.floor_points_leaders(num_results=10, round_name=round_name)
  profile_standings = Profile.points_leaders(num_results=10, round_name=round_name).select_related("scoreboardentry")
  user_floor_standings = floor.points_leaders(num_results=10, round_name=round_name).select_related("scoreboardentry")
  
  categories_list = __get_categories(user)

  return render_to_response("mobile/scoreboard/"+page+".html",{
    "page": page,
    "events": events,
    "profile":user.get_profile(),
    "floor": floor,
    "categories":categories_list,
    "current_round": round_name or "Overall",
    "floor_standings": floor_standings,
    "profile_standings": profile_standings,
    "user_floor_standings": user_floor_standings,
    "help":help,
  }, context_instance=RequestContext(request))

@never_cache
@login_required
def smartgrid(request):
  activities = ActivityBase.objects.order_by("priority")
  categories_list = __get_categories(request.user)

  return render_to_response("mobile/smartgrid/index.html", {
    "activities": activities,
    "categories":categories_list,
  }, context_instance=RequestContext(request))

@login_required
@never_cache
def sgactivities(request, category_slug):
  activities = ActivityBase.objects.order_by("priority") 
  category_slugs = ["get-started", "basic-energy", "lights-out", "make-watts", "moving-on", "opala", 
    "wet-and-wild", "pot-pourri"]
  categories = ["Get Started", "Basic Energy", "Lights Out", "Make Watts", "Moving On", "Opala",
    "Wet & Wild", "Pot Pourri"]
  i = -1
  category = ""
  reached = False
  for x in category_slugs:
    if x == string.lower(category_slug):
      category = x
      i = i + 1
      reached = True
    else:
      if reached == False:
        i = i + 1

  category_no_slug = categories[i]

  for task in activities:
    annotate_task_status(request.user, task)

  return render_to_response("mobile/smartgrid/activities.html", {
    "activities": activities,
    "category": category,
    "title": category_no_slug,
  }, context_instance=RequestContext(request))

@never_cache
@login_required
def taskdeny(request, category_slug, slug):
  """locked task denial of entry"""
  activity = get_object_or_404(ActivityBase, category__slug=category_slug, slug=slug)
  
  return render_to_response("mobile/smartgrid/denied.html", {
    "category":category_slug,
    "activity":activity,
  }, context_instance=RequestContext(request))   

@login_required
@never_cache
def task_form(request,category_slug,slug):
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
  try:
    task = get_object_or_404(ActivityBase, type=category_slug, slug=slug)
  except:
    task = get_object_or_404(ActivityBase, category__slug=category_slug, slug=slug)

  if is_unlock(user, task) != True:
    return HttpResponseRedirect(reverse("pages.mobile.views.smartgrid", args=()))

  
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
      if approval.social_email:
        ref_user = User.objects.get(email=approval.user_comment)
        ref_members = ActivityMember.objects.filter(user=ref_user, activity=task)
        for m in ref_members:
          if m.approval_status == 'approved':
            approval.social_bonus_awarded = True
      
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
    
  display_form = True if request.GET.has_key("display_form") else False
  
  return render_to_response("mobile/smartgrid/form.html", {
    "task":task,
    "category":category_slug,
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
  }, context_instance=RequestContext(request))   

@never_cache
@login_required
def task(request, category_slug, slug, sender=None):
  """individual task page"""
  user = request.user
  
  if sender is None:
    try:
      ref=request.META["HTTP_REFERER"]
      if "profile" in ref:
        sender = "profile"
      elif "events" in ref:
        sender = "events"
      else:
        sender = "sgg"  
    except:
      sender="sgg"
  floor = user.get_profile().floor
  pau = False
  question = None
  form = None
  approval = None
  can_commit = None
  member_all_count = 0
  member_floor_count = 0
  social_email = None
  social_email2 = None
  
  try:
    task = get_object_or_404(ActivityBase, category__slug=category_slug, slug=slug)
  except:
    task = get_object_or_404(ActivityBase,type=category_slug, slug=slug)

  if is_unlock(user, task) != True:
    return HttpResponseRedirect(reverse("pages.mobile.views.smartgrid", args=()))

  
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
      social_email = approval.social_email
      social_email2 = approval.social_email2
      #if approval.social_email:
      #  ref_user = User.objects.get(email=approval.user_comment)
      #  ref_members = ActivityMember.objects.filter(user=ref_user, activity=task)
      #  for m in ref_members:
      #    if m.approval_status == 'approved':
      #      approval.social_bonus_awarded = True
      
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
        form = ActivityCodeForm(initial={"social_email":social_email,"social_email2":social_email2}, request=request)

      
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
    task.available_seat = task.event_max_seat - member_all_count
    
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
  
  return render_to_response("mobile/smartgrid/task.html", {
    "task":task,
    "category":category_slug,
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
    "sender":sender,
    "reminders":reminders,
  }, context_instance=RequestContext(request))    





@never_cache
@login_required
def reminder(request, category_slug, slug, error=False):
  user = request.user
  try:
    task = get_object_or_404(ActivityBase, type='event', slug=slug)
    task = task.activity
  except ActivityBase.DoesNotExist:
    try:
      task = get_object_or_404(ActivityBase, type='excursion', slug=slug)
      task = task.activity
    except ActivityBase.DoesNotExist:
      raise Http404 
  try:
    sender =False 
    ref=request.META["HTTP_REFERER"]
    if "reminder" in ref:
      sender = True 
  except:
    sender = False
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


    return render_to_response("mobile/smartgrid/reminder.html", { 
    "reminders":reminders,
    "category_slug":category_slug,
    "type":task.type,
    "slug":slug, 
    "error":error,
    "sender":sender,
    "task":task,
  }, context_instance=RequestContext(request))    

@never_cache
@login_required
def reminder_err(request, category_slug, slug, error=False):
  reminder(category_slug,slug,error)

@login_required
def reminder_form(request, activity_type, slug, error=False):
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
          text_reminder.text_number = form.cleaned_data["text_number"]
          text_reminder.text_carrier = form.cleaned_data["text_carrier"]
          if form.cleaned_data["send_text"]:

            text_reminder.send_at = task.activity.event_date - datetime.timedelta(
                hours=int(form.cleaned_data["text_advance"])
            )
            text_reminder.save()
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
	profile.contact_text = form.cleaned_data["text_number"]
        profile.contact_carrier = form.cleaned_data["text_carrier"]
        profile.save()
        return HttpResponseRedirect(reverse('mobile_reminder',args=(slug,slug)))
        return HttpResponse(json.dumps({"success": True}), mimetype="application/json") 

      else: 
        #template = render_to_string("mobile/smartgrid/reminder.html", {
        #"reminders": {"form": form},
        #"task": task,
        #},context_instance=RequestContext(request)) 
        #return HttpResponse(json.dumps({
        #"success": False,
        #"form": template,
        #}), mimetype="application/json") 
        #return HttpResponseRedirect(reverse('mobile_reminder_error',args=( slug,slug)))
        return reminder(request,slug,slug,True)
  return HttpResponseRedirect(reverse('mobile_reminder',args=(slug,slug)))
###################################################################################################

### Private methods.
@never_cache
def __add_commitment(request, commitment_id, slug):
  """Commit the current user to the commitment."""

  category = commitment_id
  commitment = get_object_or_404(Commitment, category__slug=commitment_id, slug=slug)
  user = request.user
  floor = user.get_profile().floor
  
  members = CommitmentMember.objects.filter(user=user, commitment=commitment);
  if members.count() > 0 and members[0].days_left() == 0:
    #commitment end
    message = "Commitment: %s (Cancelled)" % commitment.title
    user.get_profile().remove_points(2, datetime.datetime.today() - datetime.timedelta(minutes=1), message)
    user.get_profile().save()
    member = members[0]
    member.award_date = datetime.datetime.today()
    member.save()
      
  if commitment not in user.commitment_set.all() and can_add_commitments(user):
    # User can commit to this commitment.
    member = CommitmentMember(user=user, commitment=commitment)
    member.save()
    # messages.info("You are now committed to \"%s\"" % commitment.title)

    #increase point
    message = "Commitment: %s (Signup)" % commitment.title
    user.get_profile().add_points(2, datetime.datetime.today() - datetime.timedelta(minutes=1), message)
    user.get_profile().save()
    
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
        
  return HttpResponseRedirect(reverse("mobile_task", args=(category, commitment.slug,)))

@never_cache
def __add_activity(request, activity_id, slug):
  """Commit the current user to the activity."""

  category = activity_id
  activity = get_object_or_404(Activity, category__slug=activity_id, slug=slug)
  user = request.user
  floor = user.get_profile().floor
  
  # Search for an existing activity for this user
  if activity not in user.activity_set.all() and request.method == "POST":

    if activity.type == 'survey':
      question = TextPromptQuestion.objects.filter(activity=activity)
      form = SurveyForm(request.POST or None, questions=question)
    
      if form.is_valid():
        for i,q in enumerate(question):
          activity_member = ActivityMember(user=user, activity=activity)
##TODO.          activity_member.user_comment = form.cleaned_data["comment"]
          activity_member.question = q
          activity_member.response = form.cleaned_data['choice_response_%s' % i]
          
          if i == (len(question)-1):
            activity_member.approval_status = "approved"
            
          activity_member.save()
      else:   # form not valid
        return render_to_response("mobile/smartgrid/task.html", {
            "task":activity,
            "category":category,
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
      message = "%s: %s (Sign up)" % (activity.type.capitalize(), activity.title)
      user.get_profile().add_points(2, datetime.datetime.today() - datetime.timedelta(minutes=1), message)
      user.get_profile().save()

    return HttpResponseRedirect(reverse("mobile_task", args=(category, activity.slug,)))

@never_cache
def __request_activity_points(request, activity_id, slug):
  """Creates a request for points for an activity."""
  
  category = activity_id
  try:
    activity = get_object_or_404(Activity, category__slug=activity_id, slug=slug)
  except:
    activity = get_object_or_404(Activity, type=activity_id, slug=slug)
  user = request.user
  floor = user.get_profile().floor
  question = None
  activity_member = None
  
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
    elif activity.confirm_type == "code":
      form = ActivityCodeForm(request.POST, request=request, activity=activity)
    else:
      form = ActivityTextForm(request.POST, request=request, activity=activity)

    ## print activity.confirm_type
    if form.is_valid():
      if not activity_member:
        activity_member = ActivityMember(user=user, activity=activity)
      
      activity_member.user_comment = form.cleaned_data["comment"]
      # Attach image if it is an image form.
      if form.cleaned_data.has_key("image_response"):
        path = activity_image_file_path(user=user, filename=request.FILES['image_response'].name)
        activity_member.image = path
        
        new_file = activity_member.image.storage.save(path, request.FILES["image_response"])
        
        activity_member.approval_status = "pending"

      elif activity.confirm_type == "code":
        # Approve the activity (confirmation code is validated in forms.ActivityTextForm.clean())
	try:
          code = ConfirmationCode.objects.get(code=form.cleaned_data["response"])
          code.is_active = False
          code.save()
          activity_member.approval_status = "approved" # Model save method will award the points.
          points = activity_member.activity.point_value
        except ConfirmationCode.DoesNotExist:
          form.response.errors="ERROR"
          return HttpResponseRedirect(reverse("mobile_task", args=(category, activity.slug,)))
      # Attach text prompt question if one is provided
      elif form.cleaned_data.has_key("question"):
        activity_member.question = TextPromptQuestion.objects.get(pk=form.cleaned_data["question"])
        activity_member.response = form.cleaned_data["response"]
        activity_member.approval_status = "pending"
                
      elif activity.confirm_type == "free":
        activity_member.response = form.cleaned_data["response"]
        activity_member.approval_status = "pending"

      activity_member.social_email = form.cleaned_data["social_email"]
      activity_member.save()
          
      return HttpResponseRedirect(reverse("mobile_task", args=(category, activity.slug,)))
    
    if activity.confirm_type == "text":
      question = activity.pick_question(user.id)
      ##if question:
      ##  form = ActivityTextForm(initial={"question" : question.pk}, question_id=question.pk)
      
    return render_to_response("mobile/smartgrid/task.html", {
    "task":activity,
    "category": category,
    "pau":False,
    "form":form,
    "question":question,
    "member_all":0,
    "member_floor":0,
    "display_form":True,
    "form_title": "Get your points",
    }, context_instance=RequestContext(request))    


###################################################################################################

@never_cache
@login_required
def sgadd(request, category_slug, slug):
 
  try:
    task = get_object_or_404(ActivityBase, type=category_slug, slug=slug)
  except:
    task = get_object_or_404(ActivityBase, category__slug=category_slug, slug=slug)


  if task.type == "commitment":
    return __add_commitment(request, category_slug, slug)
    
  if task.type == "activity":
    return __request_activity_points(request, category_slug, slug)
  elif task.type == "survey":
    return __add_activity(request, category_slug, slug)
  else: ##event 
    task = Activity.objects.get(pk=task.pk)
    if task.is_event_completed():
      return __request_activity_points(request, category_slug, slug) 
    else:  
      return __add_activity(request, category_slug, slug)
    
   
  

def landing(request):
  if request.user.is_authenticated():
    return HttpResponseRedirect(reverse("mobile_index")) 
  return render_to_response("mobile/landing.html", {}, context_instance=RequestContext(request))
 
class EventDay:
  def __init__(self):
    self.date = ''
    self.datestring = ''
    self.eventlist = []
    self.count = 0
    self.attending = False
  def __str__(self):
    return "obj= " + str(self.date) + " " +  " " + str(self.eventlist)

#used for sorting lists of events
def get_date(obj):
  return obj.event_date

@login_required
@never_cache
def events(request,option): 
  objlist = []
  user = request.user
  options = ["upcoming","attending","past"] 
  option = uniToStr(option)
  view = str.lower(option)

  #handle the date functionality
  day = timedelta(days = 1) 
  today= datetime.date(2011,07,10)
  datelist = []
  #uncomment the below line to bring things up to date
  today = date.today()
  datelist.append([])
  datelist[0].append(today)
  datelist[0].append(today.strftime("%A, %B %d"))
 
  temp = today
  for i in range(1,7,1):
    datelist.append([])
    temp += day
    datelist[i].append(temp)
    datelist[i].append(temp.strftime("%A, %B %d"))

  #upcoming
  if string.lower(option) == options[0] :
    events = get_available_events(user) 
    for element in datelist:
      obj = EventDay()
      obj.date = element[0]
      obj.datestring = element[1]
      temparray = [] 
      count = 0
      for event in events: 
        e_date = event["event_date"]
        if e_date.strftime("%B %d, %y") == obj.date.strftime("%B %d, %y"):  
          try:
            member = ActivityMember.objects.get(user=request.user,activity__id=event["id"])
            if member.approval_status == "pending":  
              event["attending"] = True
          except ActivityMember.DoesNotExist: 
            boolean = False
          temparray.append(event)
          count = count + 1  
      obj.count = count
      obj.eventlist = temparray
      objlist.append(obj)
  
  #past
  elif string.lower(option) == options[2]:   
    avail = ActivityBase.objects.filter(type='event')
    for event in avail:
      if event.activity.event_date.date() < today:
        objlist.append(event.activity) 
    objlist.sort(key=get_date)
  return render_to_response("mobile/events/index.html", {
  "view": view, 
  "objlist": objlist,
  "options": options, 
  }, context_instance=RequestContext(request))



@login_required
@never_cache
def quests(request,option): 
  questlist = []
  user = request.user
  options = ["available","accepted","completed"] 
  view = option 

  #completed
  if string.lower(option) == options[2]:
    questlist = Quest.objects.filter(questmember__user=request.user,questmember__completed=True)  

  return render_to_response("mobile/quests/index.html", {
  "view": view,
  "questlist": questlist,
  "options": options, 
  }, context_instance=RequestContext(request))

@login_required
def quest_detail(request, ref, slug):
  ref=ref.lower 
  quest=get_object_or_404(Quest,quest_slug=slug)  
  return render_to_response("mobile/quests/details.html", {
    "quest": quest,
    "referer": ref,
  }, context_instance=RequestContext(request))

@login_required
def popup(request):
  return render_to_response("mobile/quests/popup.html", {}, context_instance=RequestContext(request))

@login_required
def summary(request):
  return render_to_response("mobile/summary/index.html", {}, context_instance=RequestContext(request))

@login_required
def help(request, page):
  page = string.lower(page)
  if page == '':
    page = 'index'
  form = None
  if request.method == "POST":
    form = AskAdminForm(request.POST)
    if form.is_valid():
      user = request.user
      email = user.get_profile().contact_email or user.email
      form.success = "Your question has been sent to the Kukui Cup administrators. We will email a response to " + email
      
  if not form:
    form = AskAdminForm()
    
  rules = HelpTopic.objects.filter(category="rules", parent_topic__isnull=True)
  faqs = HelpTopic.objects.filter(category="faq", parent_topic__isnull=True)
  return render_to_response("mobile/help/"+page+".html", {
      "form": form,
      "rules": rules,
      "faqs": faqs,
  }, context_instance=RequestContext(request))

@login_required
def helptopic(request, category, slug):
  topic = get_object_or_404(HelpTopic, slug=slug, category=category)
  return render_to_response("mobile/help/topic.html", {
      "topic": topic,
  }, context_instance=RequestContext(request))

@never_cache
@login_required
def profile(request,page): 
  page = string.lower(page)
  user = request.user
  form = None
  points_logs = user.pointstransaction_set.order_by("-submission_date").all()
  if request.method == "POST":
    user = request.user
    form = ProfileForm(request.POST)
    if form.is_valid():
      profile = user.get_profile()
      profile.name = form.cleaned_data["display_name"].strip()
      profile.contact_email = form.cleaned_data["contact_email"]
      profile.contact_text = form.cleaned_data["contact_text"]
      profile.contact_carrier = form.cleaned_data["contact_carrier"]
      # profile.enable_help = form.cleaned_data["enable_help"]
        
      try:
        profile.save()
        form.message = "Your changes have been saved"
      except IntegrityError:
        form.message = "Please correct the errors below."
        form.errors.update({"display_name": "'%s' is taken, please enter another name." % profile.name})
    else:
      form.message = "Please correct the errors below."
      
  # If this is a new request, initialize the form.
  if not form:    
    form = ProfileForm(initial={
      "enable_help": user.get_profile().enable_help,
      "display_name": user.get_profile().name,
      "contact_email": user.get_profile().contact_email or user.email,
      "contact_text": user.get_profile().contact_text,
      "contact_carrier": user.get_profile().contact_carrier,
    })
    
  return render_to_response("mobile/profile/"+page+".html", {
    "profile": user.get_profile(),
    "user": user,
    "form": form, 
    "points_logs": points_logs,
    "in_progress_members": get_in_progress_members(user),
    "commitment_members": get_current_commitment_members(user),
    "completed_members": get_completed_members(user),
    "notifications": user.usernotification_set.order_by("-created_at"),
    "help_info": {
      "prefix": "profile_index",
      "count": range(0, 3),
    }
  }, context_instance=RequestContext(request))
 
def raffle(request):
  floor = request.user.get_profile().floor
  prizes = _get_prizes(floor)
  raffle_dict = _get_raffle_prizes(request.user)
    
  return render_to_response("mobile/raffle/index.html", {
      "prizes": prizes,
      "raffle": raffle_dict,
  }, context_instance=RequestContext(request))

def raffle_item(request, prize_slug):

  floor = request.user.get_profile().floor
  prizes = _get_prizes(floor)
  raffle_dict = _get_raffle_prizes(request.user)
#  prize = ""
#  for i in prizes:
#    if prize_slug == slugify(i.title):
#      prize = i

  return render_to_response("mobile/raffle/item.html", {
    "slug":prize_slug,
    "prizes":prizes,
    "raffle": raffle_dict,
  }, context_instance=RequestContext(request))

@login_required
def power_and_energy(request): 
  return render_to_response("mobile/power&energy/index.html", { 
  }, context_instance=RequestContext(request))

def attend_code(request):
  """claim the attendance code"""
  
  user = request.user
  activity_member = None
  message = None
  social_email = None
  
 #if request.is_ajax() and request.method == "POST":
  if True:
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

      if message:
        return HttpResponse(json.dumps({
          "message": message,
          "social_email": social_email
          }), mimetype="application/json")
            
      try:
        activity_member = ActivityMember.objects.get(user=user, activity=code.activity)
      except ObjectDoesNotExist:
        activity_member = ActivityMember(user=user, activity=code.activity)
        
      activity_member.approval_status = "approved" # Model save method will award the points.
      value = code.activity.point_value  

      if form.cleaned_data.has_key("social_email") and form.cleaned_data["social_email"] != "Email":
        activity_member.social_email = form.cleaned_data["social_email"]
        
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
 
def uniToStr(uni) :
  str = unicodedata.normalize('NFKD', uni).encode('ascii','ignore')
  return str





def read_notification(request, notification_id):
  if not request.method == "POST":
    raise Http404
    
  notification = get_object_or_404(UserNotification, pk=notification_id)
  notification.unread = False
  notification.save() 
  if request.META.has_key("HTTP_REFERER"):
    return HttpResponseRedirect(request.META["HTTP_REFERER"])
  else:
    return HttpResponseRedirect(reverse("mobile_index"))



@never_cache
@login_required
def drop_task(request, category_slug, slug):
  
  task = get_object_or_404(ActivityBase, type=category_slug, slug=slug)
  
  if task.type == "commitment":
    return __drop_commitment(request, task.commitment)
    
  if task.type == "event" or task.type == "excursion":
    return __drop_activity(request, task.activity)


def __drop_activity(request, activity):
  """drop the current user from the activity."""
  user = request.user
  floor = user.get_profile().floor
  
  # Search for an existing activity for this user
  if activity in user.activity_set.all():
    activity_member = user.activitymember_set.get(activity=activity)
    activity_member.delete()
        
    #decrease point
    message = "%s: %s (Drop)" % (activity.type.capitalize(), activity.title)
    user.get_profile().remove_points(2, datetime.datetime.today() - datetime.timedelta(minutes=1), message, activity_member)
    user.get_profile().save()
    value = 2
    
    response = HttpResponseRedirect(reverse("mobile_task", args=(slugify(activity.category), activity.slug,)))
    notification = "Removed from signup list. you lose " + str(value) + " points."
    response.set_cookie("task_notify", notification)
    return response

def __drop_commitment(request, commitment):
  """drop the commitment."""
  user = request.user
  floor = user.get_profile().floor

  if commitment in user.commitment_set.all():
    # User can drop this commitment.
    member = user.commitmentmember_set.get(commitment=commitment, award_date=None)
    member.delete()

    #decrease sign up point
    message = "Commitment: %s (Drop)" % (commitment.title)
    value = 2
    user.get_profile().remove_points(value, datetime.datetime.today() - datetime.timedelta(minutes=1), message, member)
    user.get_profile().save()

    response = HttpResponseRedirect(reverse("mobile_task", args=(slugify(commitment.category), commitment.slug,)))
    notification = "Commitment dropped. you lose " + str(value) + " points."
    response.set_cookie("task_notify", notification)
    return response


