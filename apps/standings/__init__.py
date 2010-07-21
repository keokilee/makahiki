from django.contrib.auth.models import User
from makahiki_profiles.models import Profile
import simplejson as json

class StandingsException(Exception):
  def __init__(self, value):
    self.value = value
    
  def __str__(self):
    return repr(self.value)
  
def get_standings_for_user(user, standings_group="floor"):
  """Generates standings for a user to be used in the standings widget.  
  Generates either floor-wide standings or standings based on all users.
  Returns a json structure for insertion into the javascript code."""
  
  user_profile = Profile.objects.get(user=user)
  standings_type = "individual"
  
  if not user_profile.floor:
    # Nothing we can do here.
    return ""
  
  if standings_group == "floor":
    profiles = Profile.objects.filter(floor=user_profile.floor).order_by("-points")
    title = "Individual standings, %s" % user_profile.floor
    
  elif standings_group == "all":
    profiles = Profile.objects.all().order_by("-points")
  else:
    raise StandingsException("Unknown standings type %s" % standings_type)
    
  info, user_index = _calculate_standings(user_profile, profiles)
  
def _calculate_user_standings(user_profile, profiles):
  """Finds user standings based on the user's profile and a list of profiles.
  Returns dictionary of points and the index of the user."""
  
  # First and last users are easy enough to retrieve.
  first = profiles[0]
  last = profiles[len(profiles)-1]
  
  # Search for user.
  rank = 1
  above_points = first.points
  below_points = last.points
  for profile in profiles:
    # Going to group together users who are tied for now.
    if profile.points > user_profile.points:
      above_points = profile.points
      rank += 1
    elif profile.points < user_profile.points:
      below_points = profile.points
      break
      
  # Construct the return dictionary.
  index = 0
  info = [{"points": first.points, "rank": 1}]
  if rank != 1:
    info.append({"points": above_points, "rank": rank - 1})
    info.append({"points": user_profile.points, "rank": rank})
    index = 2
  if user_profile.points > below_points:
    info.append({"points": below_points, "rank": rank + 1})
    info.append({"points": last.points, "rank": len(profiles)})
    
  return info, index
    
    
      
    
  
  