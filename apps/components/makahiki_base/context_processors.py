import simplejson as json
from django.conf import settings

from components.makahiki_base import get_floor_label, get_round_info, get_theme, get_current_round, get_competition_dates, in_competition
from components.makahiki_profiles.models import Profile
from components.floors.models import Floor

def competition(request):
  """Provides access to standard competition constants within a template."""
  
  # We may want to retrieve theme settings for insertion into CSS.
  theme_name, theme_dict = get_theme()
  
  # Get the number of users for the user's floor and overall.
  floor_count = Floor.objects.count()
  floor_member_count = request.user.get_profile().floor.profile_set.count()
  overall_member_count = Profile.objects.count()
  
  # Get current round info.
  current_round = get_current_round()
    
  # Get Facebook info.
  try:
    facebook_app_id = settings.FACEBOOK_APP_ID
  except AttributeError:
    facebook_app_id = None
  
  
  return {
    "COMPETITION_NAME": settings.COMPETITION_NAME,
    "COMPETITION_POINT_NAME": settings.COMPETITION_POINT_NAME or "point",
    "THEME_NAME": theme_name, 
    "THEME": theme_dict,
    "FLOOR_COUNT": floor_count,
    "FLOOR_MEMBER_COUNT": floor_member_count,
    "OVERALL_MEMBER_COUNT": overall_member_count,
    "ROUNDS": json.dumps(get_round_info()),
    "FLOOR_LABEL": get_floor_label(),
    "CURRENT_ROUND": current_round,
    "FACEBOOK_APP_ID": facebook_app_id,
  }

    
