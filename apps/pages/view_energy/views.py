from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.views.decorators.cache import never_cache

from elementtree import ElementTree
from decimal import *

from components.activities.models import *
from components.activities import *
from components.floors.models import *
from components.floors import *
from components.energy_goals import *
from components.makahiki_base import get_round_info
from pages.news.forms import WallForm

@never_cache
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
    
  helps = ["Current Lounge Power", "Overall kWh Score Board", "Daily Energy Goal Status"]
  helpfiles = ["view_energy/help1.html", "view_energy/help2.html", "view_energy/help3.html"]

  return render_to_response("energy/index.html",{
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
    