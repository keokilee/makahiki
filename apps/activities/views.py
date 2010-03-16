from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User
from activities.models import Commitment, CommitmentMember

# Create your views here.

def add_commitment(request, commitment_id):
  """Commit the current user to the commitment."""
  
  if request.method == "POST":
    commitment = get_object_or_404(Commitment, pk=commitment_id)
    user = request.user
    
    # Search for an existing commitment for this user
    if not CommitmentMember.objects.filter(user=user, commitment=commitment):
      commitment_member = CommitmentMember(user=user, commitment=commitment)
      commitment_member.save()
    # TODO: Need to notify if this commitment already exists.
    
    return HttpResponseRedirect(reverse("kukui_cup_profile.views.profile", args=(request.user.username,)))
  else:
    # TODO: Render commitment detail.
    return HttpResponseRedirect(reverse("kukui_cup_profile.views.profile", args=(request.user.username,)))
    
def remove_commitment(request, commitment_id):
  """Remove the current user's commitment."""
  
  if request.method == "POST":
    commitment = get_object_or_404(Commitment, pk=commitment_id)
    user = request.user
    commitment_member = CommitmentMember.objects.filter(user=user, commitment=commitment)
    
    if commitment_member:
      commitment_member.delete()
      return HttpResponseRedirect(reverse("kukui_cup_profile.views.profile", args=(request.user.username,)))
    else:
      # TODO: Print error message.
      return HttpResponseRedirect(reverse("kukui_cup_profile.views.profile", args=(request.user.username,)))
      
  