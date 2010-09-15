import simplejson as json

from makahiki_base import get_floor_label, get_round_info, get_theme, get_current_round

def competition(request):
  """Provides access to standard competition constants within a template."""
  
  # We may want to retrieve theme settings for insertion into CSS.
  theme = get_theme()
  
  return {
    "THEME": json.dumps(theme),
    "ROUNDS": json.dumps(get_round_info()),
    "FLOOR_LABEL": get_floor_label(),
    "CURRENT_ROUND": json.dumps(get_current_round()),
  }

    
    