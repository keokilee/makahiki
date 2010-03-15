from django.shortcuts import get_object_or_404

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
    
    return HttpResponseRedirect(reverse("apps.kukui_cup_profile.profile", args=(request.user.username,)))
  else:
    # TODO: Render commitment detail.
    return HttpResponseRedirect(reverse("apps.kukui_cup_profile.profile", args=(request.user.username,)))

  