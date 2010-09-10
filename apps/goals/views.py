import simplejson as json

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import messages

from makahiki_base import restricted
from goals.models import EnergyGoal, EnergyGoalVote
from goals.forms import EnergyGoalVotingForm

# Create your views here.

def vote(request, goal_id):
  """Adds the user's vote to the goal."""
  if request.method != "POST":
    return Http404
  
  goal = get_object_or_404(EnergyGoal, pk=goal_id)
  user = request.user
  
  form = EnergyGoalVotingForm(request.POST, instance=EnergyGoalVote(user=user, goal=goal))
  if form.is_valid():
    form.save()
    messages.info(request, 'Thank you for your vote!')
  
  if request.META.has_key("HTTP_REFERER"):
    return HttpResponseRedirect(request.META["HTTP_REFERER"]) 
    
  else:
    return HttpResponseRedirect(reverse("profile_detail", args=(user.pk,)))
  
def voting_results(request, goal_id):
  """Get the voting results for the user's floor."""
  goal = get_object_or_404(EnergyGoal, pk=goal_id)
  
  profile = request.user.get_profile()
  results = goal.get_floor_results(profile.floor)
  
  return HttpResponse(json.dumps({
      "results": list(results), # Needed to convert results from a queryset.
  }), mimetype='text/plain')
  