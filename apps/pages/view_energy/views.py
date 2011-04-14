

from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse

from elementtree import ElementTree
from decimal import *

from components.activities.models import *
from components.activities import *
from components.floors.models import *
from components.floors import *
from components.energy_goals import *
from components.makahiki_base import get_round_info
from pages.news.forms import WallForm

@login_required
def index(request):
  user = request.user
  floor = user.get_profile().floor
  golow_activities = get_available_golow_activities(user)
  golow_posts = Post.objects.filter(floor=floor, style_class="user_post").order_by("-id")[:5]
  
  standings = []

  rounds = get_round_info()
  scoreboard_rounds = []
  today = datetime.datetime.today()
  for key in rounds.keys():
    # Check if this round happened already or if it is in progress.
    # We don't care if the round happens in the future.
    if today >= datetime.datetime.strptime(rounds[key]["start"], "%Y-%m-%d"):
      # Slugify to create a div id.
      scoreboard_rounds.append(key)
  
  ## TODO. create the baseline table
  baseline = 24 
  energy = 20
  percent_reduce = 5
  power = 150
  last_update = None

  goals = FloorEnergyGoal.objects.filter(floor=floor);
  if goals.count() > 0:
    percent_reduce = goals[0].percent_reduction
  
  percent = 100 - percent_reduce  
  goal = baseline * percent / 100
  
  ### TODO. get the goal from gdata
  
  goal = 113
  energy = 119
  
  over = "over"
  diff = energy - goal
  if diff <= 0:
    over = "below"
    diff = 0 - diff
  
  bar_px = 150  
  if energy <= baseline:
    baseline_px = bar_px
    actual_px = bar_px * energy / baseline
  else:
    baseline_px = bar_px * baseline / energy
    actual_px = bar_px
  
  appliance_type = ["Playing XBox 360",
                "Using laptop",
                "Watching plasma TV",
                "Playing stereo",
                "Playing Wii",
                "Playing Playstation 3"]
  appliance_data = [185.0, 
                    70.0, 
                    300.0, 
                    100.0, 
                    20.0, 
                    195.0]
  appliances = []
  for ix in range(len(appliance_type)):
    appliances.append([appliance_type[ix], format(diff * 1000 / appliance_data[ix], ".1f")])
    
  power = format(power, '.1f')       
  energy = format(energy, '.1f')     
  diff = format(diff, '.1f')

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
      "diff":diff,
      "appliances":appliances,
      "appliance_data":appliance_data,
      "power":power,
      "last_update":last_update,
      "floor": floor,
      "scoreboard_rounds":scoreboard_rounds,
      "golow_activities":golow_activities,
      "posts":golow_posts,
      "wall_form": WallForm(),
      "help_info": {
        "prefix": "energy_index",
        "count": range(0, 3),
      }
    }
    ,context_instance=RequestContext(request))
    