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
  
  # Check if the user is refreshing from the form.
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
  
  # Check if the user is logged in and has a floor.
  elif request.user.is_authenticated() and request.user.get_profile().floor:
    floor = request.user.get_profile().floor
    form = EnergyDataSelectForm(initial={"floor": floor,})
    
    # Check if there is an energy goal available.
    goal = EnergyGoal.get_current_goal()
    if goal:
      try:
        floor_goal = goal.floorenergygoal_set.get(floor=floor)
      except FloorEnergyGoal.DoesNotExist:
        floor_goal = None
  
  # The user is either not logged in or has no default floor.  Use the first floor.
  else:
    form = EnergyDataSelectForm()
    floor = form.fields["floor"].queryset[0] # Take the first floor in the list.
  
  return render_to_response("energy_data/index.html", {
    "form": form,
    "floor": floor,
    "goal": floor_goal,
  }, context_instance = RequestContext(request))
