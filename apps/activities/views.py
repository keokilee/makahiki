import datetime

from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms.util import ErrorList

from activities.models import *
from activities.forms import ActivityTextForm, ActivityImageForm, CommitmentCommentForm
from activities import MAX_COMMITMENTS

@login_required
def list(request, item_type):
  user = request.user
  
  user_items = available_items = item_name = None
  
  if item_type == "activity":
    user_items = user.activity_set.all()
    available_items = Activity.get_available_for_user(user)
    item_name = "activities"
    
  elif item_type == "commitment":
    user_items = user.commitment_set.filter(
      commitmentmember__completed=False,
    )
    available_items = Commitment.get_available_for_user(user)
    item_name = "commitments"
    
  elif item_type == "goal":
    user_items = user.get_profile().floor.goal_set.all()
    available_items = Goal.get_available_for_user(user)
    item_name = "goals"
  
  else:
    return Http404
    
  return render_to_response('activities/list.html', {
    "user_items": user_items,
    "available_items": available_items,
    "item_name": item_name,
  }, context_instance = RequestContext(request))
  
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
    return __remove_active_commitment(request, item_id)
  elif item_type == "activity":
    return __remove_activity(request, item_id)
  else:
    raise Http404
    
@login_required
def request_points(request, item_type, item_id):
  """Request the points for a given item."""

  if item_type == "activity":
    return __request_activity_points(request, item_id)
  elif item_type == "commitment":
    return __request_commitment_points(request, item_id)
  else:
    raise Http404
    
@login_required
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
  
  # Get the number of active commitments for this user
  active_commitments = Commitment.objects.filter(
    commitmentmember__user__username=user.username,
    commitmentmember__completed=False,
  )    
  if len(active_commitments) == MAX_COMMITMENTS:
    message = "You can only have %d active commitments." % MAX_COMMITMENTS
    user.message_set.create(message=message)
  elif commitment in active_commitments:
    user.message_set.create(message="You are already committed to this commitment.")
  else:
    # User can commit to this commitment.
    member = CommitmentMember(user=user, commitment=commitment)
    member.save()
    user.message_set.create(message="You are now committed to \"%s\"" % commitment.title)
    
  return HttpResponseRedirect(reverse("kukui_cup_profile.views.profile", args=(request.user.username,)))

def __remove_active_commitment(request, commitment_id):
  """Removes a user's active commitment.  Inactive commitments cannot be removed except by admins."""
  
  commitment = get_object_or_404(Commitment, pk=commitment_id)
  user = request.user

  try:
    commitment_member = CommitmentMember.objects.get(user=user, commitment=commitment, completed=False)
    commitment_member.delete()
    user.message_set.create(message="Commitment \"%s\" has been removed." % commitment.title)
    
  except ObjectDoesNotExist:
    user.message_set.create(message="We could not remove your commitment.")
    
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
    
def __request_commitment_points(request, commitment_id):
  """Generates a form to add an optional comment."""
  commitment = get_object_or_404(Commitment, pk=commitment_id)
  user = request.user
  membership = None
  
  try:
    membership = CommitmentMember.objects.get(
      user=user, 
      commitment=commitment, 
      completed=False,
      completion_date__lte=datetime.date.today,           
    )
    
  except ObjectDoesNotExist:
    user.message_set.create(message="Either the commitment is not active or it is not completed yet.")
    return HttpResponseRedirect(reverse("kukui_cup_profile.views.profile", args=(request.user.username,)))
  
  if request.method == "POST":
    form = CommitmentCommentForm(request.POST)
    if form.is_valid():
      # Currently, nothing in the form needs validation, but just to be safe.
      membership.comment = form.cleaned_data["comment"]
      membership.completed = True
      profile = user.get_profile()
      profile.points += commitment.point_value
      profile.save()
      membership.save()
      
      message = "You have been awarded %d points for your participation!" % commitment.point_value
      user.message_set.create(message=message)
      return HttpResponseRedirect(reverse("kukui_cup_profile.views.profile", args=(request.user.username,)))
    
  form = CommitmentCommentForm()
  return render_to_response("activities/request_commitment_points.html", {
    "form": form,
    "commitment": commitment,
  }, context_instance = RequestContext(request))
    
def __request_activity_points(request, activity_id):
  """Creates a request for points for an activity."""
  
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
    else:
      form = ActivityTextForm(request.POST)
      
    if form.is_valid():
      if not activity_member:
        activity_member = ActivityMember(user=user, activity=activity)
      
      activity_member.user_comment = form.cleaned_data["comment"]
      # Attach image if it is an image form.
      if form.cleaned_data["image_response"]:
        path = activity_image_file_path(user=user, filename=request.FILES['image_response'].name)
        activity_member.image = path
        new_file = activity_member.image.storage.save(path, request.FILES["image_response"])
        activity_member.approval_status = "pending"
        user.message_set.create(message="Your request has been submitted!")
        
      # Attach text prompt question if one is provided
      elif form.cleaned_data["question"]:
        activity_member.question = TextPromptQuestion.objects.get(pk=form.cleaned_data["question"])
        activity_member.response = form.cleaned_data["response"]
        activity_member.approval_status = "pending"
        user.message_set.create(message="Your request has been submitted!")
        
      else:
        # Approve the activity (confirmation code is validated in forms.ActivityTextForm.clean())
        code = ConfirmationCode.objects.get(code=form.cleaned_data["response"])
        code.is_active = False
        code.save()
        activity_member.approval_status = "approved" # Model save method will award the points.
        points = activity_member.activity.point_value
        message = "You have been awarded %d points for your participation!" % points
        user.message_set.create(message=message)

      activity_member.save()
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
      
  return render_to_response("activities/request_activity_points.html", {
    "form": form,
    "activity": activity,
    "question" : question,
    "admin_message": admin_message,
  }, context_instance = RequestContext(request))

