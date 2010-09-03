import simplejson as json
from makahiki_base import get_floor_label, get_round_info

def competition(request):
  """Provides access to standard competition constants within a template."""
  
  return_dict = {}
  return_dict.update({"ROUNDS": json.dumps(get_round_info())})
  return_dict.update({"floor_label": get_floor_label()})
  
  return return_dict