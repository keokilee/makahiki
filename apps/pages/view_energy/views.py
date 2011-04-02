from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from elementtree import ElementTree
from decimal import *

from components.activities.models import *
from components.activities import *
from components.floors.models import *
from components.floors import *
from components.energy_goals import *

from lib.restclient.restful_lib import *

@login_required
def index(request):
  user = request.user
  floor = user.get_profile().floor
  golow_activities = get_available_golow_activities(user)
  golow_posts = Post.objects.filter(floor=floor, style_class="user_post")[:10]
  
  standings = []
  
  # wattdepot rest api call
  conn = Connection("http://server.wattdepot.org:8182/wattdepot/")
  ## conn = Connection("http://localhost:8182/wattdepot/")
  
  for f in Floor.objects.all():
    wdsource = "SIM_UH_" + f.dorm.name.upper() + "_FLOORS_" + f.slug
    floor_data_resp = conn.request_get("sources/" + wdsource + "/sensordata/latest")
    xmlString = floor_data_resp['body']
    dom = ElementTree.XML(xmlString)  
    for prop in dom.getiterator('Property'):
      if prop.findtext('Key') == 'powerConsumed' and f==floor:
        power = Decimal(prop.findtext('Value'))    # in W
      if prop.findtext('Key') == 'energyConsumedToDate':
        floor_energy = Decimal(prop.findtext('Value'))   # in kWh
        standings.append([format(floor_energy / 1000,'.2f'), f])
        if f==floor:
          energy = floor_energy
    if f==floor:
      last_update = dom.findtext('Timestamp')
  
  standings.sort()
  
  ## TODO. create the baseline table
  baseline = 24 
  energy = 22
  percent_reduce = 0;
  
  goals = FloorEnergyGoal.objects.filter(floor=floor);
  if goals.count() > 0:
    percent_reduce = goals[0].percent_reduction
  
  percent = 100 - percent_reduce  
  goal = baseline * percent / 100
  over = energy - goal
  
  bar_px = 150  
  if energy <= baseline:
    baseline_px = bar_px
    actual_px = bar_px * energy / baseline
  else:
    baseline_px = bar_px * baseline / energy
    actual_px = bar_px
  
  power_max = 1000    
  power = format(power, '.2f')        ## convert to kW if need
  energy = format(energy, '.2f')      ## convert to kWh if needed
  over = format(over, '.2f')
  
  helps = ["Current Lounge Power", "Overall kWh Score Board", "Daily Energy Goal Status"]
  helpfiles = ["view_energy/help1.html", "view_energy/help2.html", "view_energy/help3.html"]

  return render_to_response("energy/index.html",{
      "baseline": baseline,
      "goal":goal,
      "actual":energy,
      "percent":percent,
      "percent_reduce":percent_reduce,
      "actual_px":actual_px,
      "baseline_px":baseline_px,
      "over":over,
      "power":power,
      "power_max":power_max,
      "last_update":last_update,
      "floor": floor,
      "standings":standings[:10],
      "golow_activities":golow_activities,
      "posts":golow_posts,
      "help_info": {
        "prefix": "energy_index",
        "count": range(0, 3),
      }
    }
    ,context_instance=RequestContext(request))