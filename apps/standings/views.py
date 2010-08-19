# Create your views here.
import datetime

from django.conf import settings
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from floors.models import Dorm
from standings import get_all_standings, MAX_INDIVIDUAL_STANDINGS

from django.views.decorators.cache import never_cache
  
@never_cache
def index(request, dorm_slug=None):
  """
  Creates the standings view for a dorm. This contains the energy standings, the floor standings, and the individual standings.
  If a dorm is not specified, standings across all dorms are retrieved.
  """
  
  dorm = None
  current_page = "floor"
  if settings.COMPETITION_GROUP_NAME:
    name = settings.COMPETITION_GROUP_NAME
    title = name.capitalize() + " vs. " + name.capitalize()
  else:
    title = "Floor vs. Floor"
  if dorm_slug:
    dorm = get_object_or_404(Dorm, slug=dorm_slug)
    current_page = dorm.slug
    title = dorm.name
    
  # Retrieve dorms for use in subnavigation.
  dorms = Dorm.objects.all()
  
  # Default selected tab to overall.
  standings_titles = []
  today = datetime.datetime.today()
  
  rounds = settings.COMPETITION_ROUNDS
  selected_tab = len(rounds)
  for index, key in enumerate(rounds.keys()):
    standings_titles.append(key)
    
    start = datetime.datetime.strptime(rounds[key]["start"], "%Y-%m-%d")
    end = datetime.datetime.strptime(rounds[key]["end"], "%Y-%m-%d")
    if today >= start and today < end:
      selected_tab = index
    
  standings_titles.append("Overall")
  
    
  # Retrieve the standings
  floor_standings = get_all_standings(dorm=dorm, grouping="floor")
  individual_standings = get_all_standings(dorm=dorm, grouping="individual", count=MAX_INDIVIDUAL_STANDINGS)
  
  return render_to_response('standings/standings.html', {
    "current_page": current_page,
    "title": title,
    "dorms": dorms,
    "floor_points": floor_standings,
    "individual_points": individual_standings,
    "standings_titles": standings_titles,
    "selected_tab": selected_tab,
  }, context_instance = RequestContext(request))
  
