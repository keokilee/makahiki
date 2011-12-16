from elementtree import ElementTree
from decimal import *

from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.views.decorators.cache import never_cache
from django.shortcuts import get_object_or_404
from django.db.models import Count, F

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
  golow_posts = Post.objects.filter(floor=floor, style_class="user_post").select_related('user__profile').order_by("-id")[:5]
  
  standings = []

  rounds = get_round_info()
  scoreboard_rounds = []
  today = datetime.datetime.today()
  for key in rounds.keys():
    # Check if this round happened already or if it is in progress.
    # We don't care if the round happens in the future.
    if today >= datetime.datetime.strptime(rounds[key]["start"], "%Y-%m-%d"):
      scoreboard_rounds.append(key)
      
  # Generate the scoreboard for energy goals.
  # We could aggregate the energy goals in floors, but there's a bug in Django.
  # See https://code.djangoproject.com/ticket/13461
  goals_scoreboard = FloorEnergyGoal.objects.filter(
      actual_usage__lte=F("goal_usage")
  ).values(
      "floor__number", 
      "floor__dorm__name"
  ).annotate(completions=Count("floor")).order_by("-completions")
  
    
  return render_to_response("energy/index.html",{
      "floor": floor,
      "scoreboard_rounds":scoreboard_rounds,
      "golow_activities":golow_activities,
      "posts":golow_posts,
      "wall_form": WallForm(),
      "goals_scoreboard": goals_scoreboard,
  }, context_instance=RequestContext(request))
    