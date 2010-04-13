from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.template import RequestContext

from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from activities.models import *
from activities.forms import ActivityTextForm, ActivityImageForm 
from django.forms.util import ErrorList

@login_required
def add_participation(request, item_type, item_id):
  """Adds the user as participating in the item."""
  
  if not request.method == "POST":
    request.user.message_set.create(message="We could not process your request.  Please try again.")
    return HttpResponseRedirect(reverse("kukui_cup_profile.views.profile", args=(request.user.username,)))
  elif item_type == "commitment":
    return __add_commitment(request, item_id)
  elif item_type == "activity":
    return __add_activity(request, item_id)
  else:
    raise Http404

@login_required
def remove_participation(request, item_type, item_id):
  """Removes the user's participation in the item."""
  
  if not request.method == "POST":
    request.user.message_set.create(message="We could not process your request.  Please try again.")
    return HttpResponseRedirect(reverse("kukui_cup_profile.views.profile", args=(request.user.username,)))
  elif item_type == "commitment":
    return __remove_commitment(request, item_id)
  elif item_type == "activity":
    return __remove_activity(request, item_id)
  else:
    raise Http404
    
@login_required
def request_points(request, item_type, item_id):
  """Request the points for a given item."""

  if item_type == "activity":
    return __request_points_activity(request, item_id)
  else:
    raise Http404
    
def view_codes(request, activity_id):
  """View the confirmation codes for a given activity."""
  
  if not request.user or not request.user.is_staff:
    raise Http404
    
  activity = get_object_or_404(Activity, pk=activity_id)
  codes = ConfirmationCode.objects.filter(activity=activity)
  if len(codes) == 0:
    raise Http404
  
  return render_to_response("activities/view_codes.html", {
    "activity": activity,
    "codes": codes,
  }, context_instance = RequestContext(request))

### Private methods.

def __add_commitment(request, commitment_id):
  """Commit the current user to the commitment."""
  
  commitment = get_object_or_404(Commitment, pk=commitment_id)
  user = request.user
  
  # Search for an existing commitment for this user
  if not CommitmentMember.objects.filter(user=user, commitment=commitment):
    commitment_member = CommitmentMember(user=user, commitment=commitment)
    commitment_member.save()
    user.message_set.create(message="Added the commitment \"" + commitment.title + "\"")
  else:
    user.message_set.create(message="You are already committed to this commitment.")
    
  return HttpResponseRedirect(reverse("kukui_cup_profile.views.profile", args=(request.user.username,)))

def __remove_commitment(request, commitment_id):
  """Remove the current user's commitment."""
  
  commitment = get_object_or_404(Commitment, pk=commitment_id)
  user = request.user
  commitment_member = CommitmentMember.objects.filter(user=user, commitment=commitment)
  
  if commitment_member:
    commitment_member.delete()
    user.message_set.create(message="Removed the commitment \"" + commitment.title + "\"")
    return HttpResponseRedirect(reverse("kukui_cup_profile.views.profile", args=(request.user.username,)))
  else:
    user.message_set.create(message="You are not committed to this commitment.")
    return HttpResponseRedirect(reverse("kukui_cup_profile.views.profile", args=(request.user.username,)))

def __add_activity(request, activity_id):
  """Commit the current user to the activity."""

  activity = get_object_or_404(Activity, pk=activity_id)
  user = request.user

  # Search for an existing activity for this user
  if not ActivityMember.objects.filter(user=user, activity=activity):
    activity_member = ActivityMember(user=user, activity=activity, approval_status="unapproved")
    activity_member.save()
    user.message_set.create(message="You are now participating in the activity \"" + activity.title + "\"")
  else:
    user.message_set.create(message="You are already participating in this activity.")

  return HttpResponseRedirect(reverse("kukui_cup_profile.views.profile", args=(request.user.username,)))

def __remove_activity(request, activity_id):
  """Remove the current user's activity."""

  activity = get_object_or_404(Activity, pk=activity_id)
  user = request.user
  activity_member = ActivityMember.objects.filter(user=user, activity=activity)

  if activity_member:
    activity_member.delete()
    user.message_set.create(message="Your participation in the activity \"" + activity.title + "\" has been removed")
    return HttpResponseRedirect(reverse("kukui_cup_profile.views.profile", args=(request.user.username,)))
  else:
    user.message_set.create(message="You are not participating in this activity")
    return HttpResponseRedirect(reverse("kukui_cup_profile.views.profile", args=(request.user.username,)))
    
def __request_points_activity(request, activity_id):
  activity = get_object_or_404(Activity, pk=activity_id)
  user = request.user
  question = None
  activity_member = None
  
  try:
    # Retrieve an existing activity member object if it exists.
    activity_member = ActivityMember.objects.get(user=user, activity=activity)
    if activity_member.awarded:
      user.message_set.create(message="You have already received the points for this activity.")
      return HttpResponseRedirect(reverse("kukui_cup_profile.views.profile", args=(request.user.username,)))
      
  except ObjectDoesNotExist:
    pass # Ignore for now.

  if request.method == "POST":
    if activity.confirm_type == "image":
      form = ActivityImageForm(request.POST, request.FILES)
      if form.is_valid():
        if not activity_member:
          activity_member = ActivityMember(user=user, activity=activity)
          
        path = activity_image_file_path(user=user, filename=request.FILES['image_response'].name)
        activity_member.user_comment = form.cleaned_data["comment"]
        activity_member.image = path
        new_file = activity_member.image.storage.save(path, request.FILES["image_response"])
        activity_member.approval_status = "pending"
        activity_member.save()
        user.message_set.create(message="Your request has been submitted!")
        return HttpResponseRedirect(reverse("kukui_cup_profile.views.profile", args=(request.user.username,)))
        
    else:
      form = ActivityTextForm(request.POST)
      if form.is_valid():
        if not activity_member:
          activity_member = ActivityMember(user=user, activity=activity)
          
        activity_member.user_comment = form.cleaned_data["comment"]
        # Retrieve the question if one exists.
        if form.cleaned_data["question"]:
          activity_member.question = TextPromptQuestion.objects.get(pk=form.cleaned_data["question"])
          activity_member.response = form.cleaned_data["response"]
          activity_member.approval_status = "pending"
          activity_member.save()
          user.message_set.create(message="Your request has been submitted!")
          return HttpResponseRedirect(reverse("kukui_cup_profile.views.profile", args=(request.user.username,)))
          
        # Else, approve the activity (code is validated in forms.ActivityTextForm.clean())
        else:
          code = ConfirmationCode.objects.get(code=form.cleaned_data["response"])
          code.is_active = False
          code.save()
          activity_member.approval_status = "approved"
          # Model save method will award the points.
          activity_member.save()

          points = activity_member.activity.point_value
          message = "You have been awarded %d points for your participation!" % points
          user.message_set.create(message=message)
          return HttpResponseRedirect(reverse("kukui_cup_profile.views.profile", args=(request.user.username,)))
            
    
  elif activity.confirm_type == "image":
    form = ActivityImageForm()
  elif activity.confirm_type == "text":
    question = activity.pick_question()
    form = ActivityTextForm(initial={"question" : question.pk})
  else:
    form = ActivityTextForm()
    
  admin_message = None
  if activity_member:
    admin_message = activity_member.admin_comment
      
  return render_to_response("activities/request_points.html", {
    "form": form,
    "activity": activity,
    "question" : question,
    "item_type": "activity",
    "admin_message": admin_message,
  }, context_instance = RequestContext(request))
  

