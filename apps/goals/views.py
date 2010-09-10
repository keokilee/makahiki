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
  url = _generate_chart_url(results)
  
  return HttpResponse(json.dumps({
      "results": list(results), # Needed to convert results from a queryset.
      "url": url,
  }), mimetype='application/json')
  
def _generate_chart_url(results):
  """Helper method to generate a chart url given the goal's voting results."""
  # Create base url.
  base_url = "http://chart.apis.google.com/chart?cht=bhs&chs=150x100&chxt=x,y&chtt=Voting%20Results"
  
  # Construct the data and label parameters
  data = "&chd=t:"
  label = "&chxl=1:"
  max_votes = 0
  for result in results:
    if result["votes"] > max_votes:
      max_votes = result["votes"]
      
    label += "|%d%%" % result["percent_reduction"]
    data += "%d," % result["votes"]
    
  # Remove last comma from the data parameter.
  data = data[0:len(data)-1]
  
  # Add range parameter.
  data_range = "&chxr=0,0,%d&chds=0,%d" % (max_votes, max_votes)
  
  # Add background color parameter.
  bg_color = "&chf=bg,s,F5F3E5"
  
  # Add data color.
  data_color = "&chco=459E00"
  
  return base_url + data + label + data_range + bg_color + data_color
  
  