from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.contrib import messages

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
  
  return HttpResponseRedirect(request.META["HTTP_REFERER"]) 
  