import simplejson as json
from django.conf import settings

from components.makahiki_notifications import get_unread_notifications
from components.makahiki_base import get_floor_label, get_rounds_for_header, get_theme, get_current_round, get_competition_dates, in_competition
from components.makahiki_profiles.models import Profile
from components.floors.models import Floor
from components.quests import get_quests

def competition(request):
  """Provides access to standard competition constants within a template."""
  user = request.user
  
  # We may want to retrieve theme settings for insertion into CSS.
  theme_name, theme_dict = get_theme()
  
  # Get user-specific information.
  floor_count = Floor.objects.count()
  overall_member_count = Profile.objects.count()
  floor_member_count = None
  quests = None
  notifications = None
  
  if user.is_authenticated():
    quests = get_quests(user)
    notifications = get_unread_notifications(user, limit=3)
    if user.get_profile().floor:
      floor_member_count = user.get_profile().floor.profile_set.count()
  
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
    "ROUNDS": get_rounds_for_header(),
    "FLOOR_LABEL": get_floor_label(),
    "CURRENT_ROUND": current_round,
    "FACEBOOK_APP_ID": facebook_app_id,
    "QUESTS": quests,
    "NOTIFICATIONS": notifications,
  }

