from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse

from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from activities.models import Commitment, CommitmentMember, Activity, ActivityMember

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
  
  if not request.method == "POST":
    request.user.message_set.create(message="We could not process your request.  Please try again.")
  elif item_type == "activity":
    return __request_points_activity(request, item_id)
  else:
    raise Http404

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

  try:
    activity_member = ActivityMember.objects.get(user=user, activity=activity)
    activity_member.approval_status="pending"
    activity_member.save()
    user.message_set.create(message="Your request has been submitted.")
  except ActivityMember.DoesNotExist:
    user.message_set.create(message="You need to be participating in this activity.")
  
  return HttpResponseRedirect(reverse("kukui_cup_profile.views.profile", args=(request.user.username,)))

