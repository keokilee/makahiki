import datetime
from django.db.models.query_utils import Q
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
from django.core.cache import cache

from components.makahiki_base import get_current_round
from pages.view_activities.forms import *
from components.activities.models import *
from components.activities import *
from components.floors.models import *
from components.floors import *
from components.makahiki_profiles.models import *
from components.makahiki_profiles import *

from django.db import connection

MAX_INDIVIDUAL_STANDINGS = 10
ACTIVITIES_COL_COUNT = 3

@never_cache
@login_required
def index(request):
  user = request.user

  events = cache.get('user_events-%s' % user.username)
  if not events:
    events = get_available_events(user)
    # Cache the user_event for a day
    cache.set('user_events-%s' % user.username,
      events, 60 * 60 * 24)

  floor = user.get_profile().floor
  user_floor_standings = None
  
  current_round = get_current_round()
  round_name = current_round if current_round else None
  floor_standings = Floor.floor_points_leaders(num_results=10, round_name=round_name)
  profile_standings = Profile.points_leaders(num_results=10, round_name=round_name)
  if floor:
    user_floor_standings = floor.points_leaders(num_results=10, round_name=round_name)
  
  categories_list = __get_categories(user)

  hide_about = False
  ##TODO Check for the about cookie.
  ##if request.COOKIES.has_key("grid-hide-about"):
  ##  hide_about = True
 
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
    "hide_about": hide_about,
    "event_form": form,
  }, context_instance=RequestContext(request))

## new design, return the category list with the tasks info
def __get_categories(user):
  categories = cache.get('smartgrid-categories-%s' % user.username)
  if not categories:
      cursor = connection.cursor()

      cursor.execute('''SELECT  activities_activitymember.activity_id,
            activities_activitybase.slug as slug,
            activities_commonactivityuser.approval_status,
            activities_commonactivityuser.award_date
          FROM activities_activitymember
          INNER JOIN activities_commonactivityuser
            ON (activities_activitymember.commonactivityuser_ptr_id = activities_commonactivityuser.id)
          INNER JOIN ACTIVITIES_ACTIVITYBASE
            ON (activities_activitymember.activity_id = activities_activitybase.id)
          WHERE activities_activitymember.user_id = %s ''' % (user.id))

      activity_members = _dictfetchall(cursor)

      cursor.execute('''SELECT  activities_commitmentmember.commitment_id,
            activities_activitybase.slug as slug,
            activities_commitmentmember.completion_date,
            activities_commitmentmember.award_date
          FROM activities_commitmentmember
          INNER JOIN ACTIVITIES_ACTIVITYBASE
            ON (activities_commitmentmember.commitment_id = activities_activitybase.id)
          WHERE activities_commitmentmember.user_id = %s ''' % (user.id))

      commitment_members = _dictfetchall(cursor)

      cursor.execute('''SELECT activities_activitybase.category_id,
            activities_activitybase.id,
            activities_activitybase.type,
            activities_activitybase.depends_on,
            activities_activitybase.depends_on_text,
            activities_activitybase.slug,
            activities_activitybase.name,
            activities_activity.event_date,
            activities_activity.point_value as 'activity_point_value',
            activities_activity.point_range_start,
            activities_activity.point_range_end,
            activities_commitment.point_value as 'commitment_point_value'
          FROM activities_activitybase
          LEFT JOIN activities_activity
            ON (activities_activity.activitybase_ptr_id = activities_activitybase.id)
          LEFT JOIN activities_commitment
            ON (activities_commitment.activitybase_ptr_id = activities_activitybase.id)
          ORDER BY activities_activitybase.category_id ASC, activities_activitybase.priority ASC''')

      tasks = _dictfetchall(cursor)
      for task in tasks:
          annotate_simple_task_status(user, task, activity_members, commitment_members)

      categories = Category.objects.all()
      for cat in categories:
        task_list = []
        for task in tasks:
          if task["category_id"]==cat.id:
            task_list.append(task)
        cat.task_list = task_list

      # Cache the categories for an hour (or until they are invalidated)
      cache.set('smartgrid-categories-%s' % user.username,
        categories, 60 * 60)

  return categories
    
def _dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

@never_cache
@login_required
def view_codes(request, slug):
  """View the confirmation codes for a given activity."""
  if not request.user or not request.user.is_staff:
    raise Http404
    
  per_page = 10
  # Check for a rows parameter
  if request.GET.has_key('rows'):
    per_page = int(request.GET['rows'])
    
  activity = get_object_or_404(Activity, slug=slug)
  codes = ConfirmationCode.objects.filter(activity=activity)
  if len(codes) == 0:
    raise Http404
  
  return render_to_response("view_activities/view_codes.html", {
    "activity": activity,
    "codes": codes,
    "per_page": per_page,
  }, context_instance = RequestContext(request))
  
@never_cache
@login_required
def view_rsvps(request, slug):
  if not request.user or not request.user.is_staff:
    raise Http404
    
  print slug
  activity = get_object_or_404(Activity, slug=slug)
  rsvps = ActivityMember.objects.filter(
      activity=activity, 
      approval_status='pending'
  ).order_by('user__last_name', 'user__first_name')
  
  return render_to_response("view_activities/rsvps.html", {
      "activity": activity,
      "rsvps": rsvps,
  }, context_instance=RequestContext(request))
  
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
        code = ConfirmationCode.objects.get(code=form.cleaned_data["response"].lower())
     
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

      response = HttpResponse(json.dumps({
        "type":code.activity.type,
        "slug":code.activity.slug,
      }), mimetype="application/json")
      notification = "You just earned " + str(value) + " points."
      response.set_cookie("task_notify", notification)
      return response
          
    # At this point there is a form validation error.
    return HttpResponse(json.dumps({
        "message": "Please input code."
    }), mimetype="application/json")
  
  raise Http404
            
### Private methods.
def __add_commitment(request, commitment):
  """Commit the current user to the commitment."""
  user = request.user
  value = None
  form = None

  if request.method == "POST":
    form = CommitmentCommentForm(request.POST, request=request, activity=commitment)
    if not form.is_valid():
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

  # now we either have a valid form or a GET
  if is_pending_commitment(user, commitment):
     member = user.commitmentmember_set.get(commitment=commitment, award_date=None)
     #commitment end, award full point
     member.award_date = datetime.datetime.today()

     if form.cleaned_data["social_email"]:
       member.social_email = form.cleaned_data["social_email"]
     if form.cleaned_data["social_email2"]:
       member.social_email2 = form.cleaned_data["social_email2"]
     member.save()
     value = commitment.point_value

  elif can_add_commitments(user):
     # User can commit to this commitment. allow to commit to completed commitment again as long as the pending does not reach max
     member = CommitmentMember(user=user, commitment=commitment)

     if form:
        member.social_email = form.cleaned_data["social_email"]
        member.social_email2 = form.cleaned_data["social_email2"]

     member.save()
     # messages.info("You are now committed to \"%s\"" % commitment.title)

     #increase the point from signup
     message = "Commitment: %s (Sign up)" % (commitment.title)
     user.get_profile().add_points(2, datetime.datetime.today() - datetime.timedelta(minutes=1), message, member)
     user.get_profile().save()
     value = 2

  response = HttpResponseRedirect(reverse("activity_task", args=(commitment.type, commitment.slug,)))
  notification = "You just earned " + str(value) + " points."
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

    response = HttpResponseRedirect(reverse("activity_task", args=(commitment.type, commitment.slug,)))
    notification = "Commitment dropped. you lose " + str(value) + " points."
    response.set_cookie("task_notify", notification)
    return response


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
      message = "%s: %s (Sign up)" % (activity.type.capitalize(), activity.title)
      user.get_profile().add_points(2, datetime.datetime.today() - datetime.timedelta(minutes=1), message, activity_member)
      user.get_profile().save()
      value = 2

    response = HttpResponseRedirect(reverse("activity_task", args=(activity.type, activity.slug,)))
    notification = "You just earned " + str(value) + " points."
    response.set_cookie("task_notify", notification)
    return response


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
    
    response = HttpResponseRedirect(reverse("activity_task", args=(activity.type, activity.slug,)))
    notification = "Removed from signup list. you lose " + str(value) + " points."
    response.set_cookie("task_notify", notification)
    return response


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
      form = ActivityImageForm(request.POST, request.FILES, request=request, activity=activity)
    elif activity.confirm_type == "free":
      form = ActivityFreeResponseForm(request.POST, request=request, activity=activity)
    elif activity.confirm_type == "free_image":
      form = ActivityFreeResponseImageForm(request.POST, request.FILES, request=request, activity=activity)
    elif activity.confirm_type == "code":
      form = ActivityCodeForm(request.POST, request=request, activity=activity)
    else:
      form = ActivityTextForm(request.POST, request=request, activity=activity)
    
    ## print activity.confirm_type
    if form.is_valid():
      if not activity_member:
        activity_member = ActivityMember(user=user, activity=activity)
      
      # Attach image if it is an image form.
      if form.cleaned_data.has_key("image_response"):
        if activity.confirm_type == "free_image":
          activity_member.response = form.cleaned_data["response"]

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
        value = activity.point_value

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

      response = HttpResponseRedirect(reverse("activity_task", args=(activity.type, activity.slug,)))
      if value:
          notification = "You just earned " + str(value) + " points."
          response.set_cookie("task_notify", notification)
          
      return response

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
  task = get_object_or_404(ActivityBase, type=activity_type, slug=slug)
  # Check here for mobile redirect.
  if request.mobile and not request.COOKIES.has_key("mobile-desktop"):
    return HttpResponseRedirect(reverse("mobile_task", args=(task.category.slug, slug)))
    
  user = request.user
  
  floor = user.get_profile().floor
  pau = False
  question = None
  form = None
  approval = None
  can_commit = None
  social_email = None
  social_email2 = None

  if is_unlock_from_cache(user, task) != True:
    return HttpResponseRedirect(reverse("pages.view_activities.views.index", args=()))
  
  if task.type != "commitment":
    task = task.activity
    hours = task.duration / 60
    minutes = task.duration % 60
    task.duration = ""
    if hours > 1:
      task.duration = "%d hours" % (hours)
    elif hours > 0: 
      task.duration = "%d hour" % (hours)
      
    if minutes > 0:
      task.duration = task.duration + " %d minutes" % (minutes)

    count = 0
    if task.type == "survey":
      member_all = ActivityMember.objects.exclude(user=user).filter(activity=task, approval_status="approved")
      members = ActivityMember.objects.filter(user=user, activity=task, approval_status="approved")
    else:
      member_all = ActivityMember.objects.filter(activity=task)
      members = ActivityMember.objects.filter(user=user, activity=task)
      count =  members.count()

    if count == 0 and task.is_group:
        members = ActivityMember.objects.filter(Q(social_email=user.email)|Q(social_email2=user.email), activity=task)
        count = members.count()

    if count > 0:
      pau = True
      approval = members[0]
      social_email = approval.social_email
      social_email2 = approval.social_email2
      if not task.has_variable_points:
        approval.points_awarded = task.point_value

    if task.type == "survey":
      question = TextPromptQuestion.objects.filter(activity=task)
      form = SurveyForm(questions=question)    
      form_title = "Survey"
    else:
      form_title = "Get your points"
    
      # Create activity request form.
      if task.confirm_type == "image":
        form = ActivityImageForm(initial={"social_email":social_email,"social_email2":social_email2}, request=request)
      elif task.confirm_type == "text":
        question = task.pick_question(user.id)
        if question:
          form = ActivityTextForm(initial={"question" : question.pk,"social_email":social_email,"social_email2":social_email2},question_id=question.pk,request=request)
      elif task.confirm_type == "free":
        form = ActivityFreeResponseForm(initial={"social_email":social_email,"social_email2":social_email2}, request=request)
      elif task.confirm_type == "free_image":
        form = ActivityFreeResponseImageForm(initial={"social_email":social_email,"social_email2":social_email2}, request=request)
      else:
        form = ActivityCodeForm(initial={"social_email":social_email,"social_email2":social_email2}, request=request)

      if task.type == "event" or task.type == "excursion":
        if not pau:
          form_title = "Sign up for this "+task.type
        
  else:  ## "Commitment"
    task = task.commitment
    members = CommitmentMember.objects.filter(user=user, commitment=task).order_by("-updated_at");
    if members.count() > 0:
      pau = True
      approval = members[0]
      social_email = approval.social_email
      social_email2 = approval.social_email2
      approval.points_awarded = task.point_value
      
    member_all = CommitmentMember.objects.filter(commitment=task);
    form_title = "Make this commitment"
    form = CommitmentCommentForm(initial={"social_email":social_email,"social_email2":social_email2}, request=request)
    can_commit = can_add_commitments(user) and not is_pending_commitment(user, task)
    
  floor_members = member_all.select_related('user__profile').filter(user__profile__floor=floor)
  member_all_count = member_all.count()

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

  return render_to_response("view_activities/task.html", {
    "task":task,
    "pau":pau,
    "approval":approval,
    "form":form,
    "question":question,
    "member_all":member_all_count,
    "floor_members": floor_members,
    "display_form":display_form,
    "form_title": form_title,
    "can_commit":can_commit,
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
   
  
