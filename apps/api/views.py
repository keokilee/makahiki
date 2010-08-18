import competition_settings
import simplejson as json

from django.http import HttpResponse, Http404

from standings import get_all_standings
from floors.models import Dorm

def rounds(request):
  """Returns a dictionary containing competition dates."""
  
  if request.method == "GET":
    rounds = competition_settings.COMPETITION_ROUNDS
    rounds.update({"start": competition_settings.COMPETITION_START, "end": competition_settings.COMPETITION_END})

    return HttpResponse(json.dumps(rounds), mimetype='application/json')
  
  # We aren't supporting other request types for now.
  raise Http404
    
def standings(request, grouping):
  """
  Gets the standings and returns them in a JSON formatted string. Takes a group parameter that is either floor or individual.
  """
  
  # Verify we have a grouping parameter and that it is either "floors" or "individuals".
  if not grouping or (grouping != "floor" and grouping != "individual"):
    raise Http404
    
  if request.method == "GET":
    dorm = None
    if request.GET.has_key("dorm"):
      dorm = Dorm.objects.get(name=request.GET["dorm"])
      
    standings = get_all_standings(dorm=dorm, grouping=grouping)
    # standings is an Python array of JSON strings, so using simplejson would double-encode this.
    standings = "[" + ",".join(standings) + "]"
    return HttpResponse(standings, mimetype='application/json')
  
  raise Http404
    