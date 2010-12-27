import simplejson as json
from django.conf import settings

from components.makahiki_base import get_floor_label, get_round_info, get_theme, get_current_round, get_competition_dates, in_competition

def competition(request):
  """Provides access to standard competition constants within a template."""
  
  # We may want to retrieve theme settings for insertion into CSS.
  theme_name, theme_dict = get_theme()
  
  # Get current round info.
  current_phase = get_current_round()
  if not current_phase and in_competition():
    current_phase = get_competition_dates()
    
  facebook_app_id = settings.FACEBOOK_APP_ID
  
  return {
    "COMPETITION_NAME": settings.COMPETITION_NAME,
    "COMPETITION_POINT_NAME": settings.COMPETITION_POINT_NAME or "point",
    "THEME_NAME": theme_name, 
    "THEME": theme_dict,
    "ROUNDS": json.dumps(get_round_info()),
    "FLOOR_LABEL": get_floor_label(),
    "CURRENT_PHASE": current_phase,
    "FACEBOOK_APP_ID": facebook_app_id,
  }

    
    