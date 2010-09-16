import simplejson as json

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.http import HttpResponse

from energy_data.forms import EnergyDataSelectForm
from goals.models import EnergyGoal, FloorEnergyGoal

# Create your views here.

def index(request):
  """Creates and/or processes the EnergyData form."""
  floor = None
  floor_goal = None
  if request.GET.has_key("floor"):
    form = EnergyDataSelectForm(request.GET)
    if form.is_valid():
      floor = form.cleaned_data["floor"]
      
      # Check if there is an energy goal available.
      goal = EnergyGoal.get_current_goal()
      if goal:
        try:
          floor_goal = goal.floorenergygoal_set.get(floor=floor)
        except FloorEnergyGoal.DoesNotExist:
          floor_goal = None
  
  # Create the empty form.
  else:
    form = EnergyDataSelectForm()
  
  return render_to_response("energy_data/index.html", {
    "form": form,
    "floor": floor,
    "goal": floor_goal,
  }, context_instance = RequestContext(request))
