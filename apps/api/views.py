import competition_settings
import simplejson as json

def rounds(self):
  """Returns a dictionary containing competition dates."""
  
  rounds = competition_settings.COMPETITION_ROUNDS
  rounds.update({"start": competition_settings.COMPETITION_START, "end": competition_settings.COMPETITION_END})
  
  return HttpResponse(json.dumps({
      "info": rounds,
  }), mimetype='application/json')
  