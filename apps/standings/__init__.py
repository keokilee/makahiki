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
    profiles = Profile.objects.filter(floor=user_profile.floor).order_by("-points", "-last_awarded_submission")
    title = "Individual standings, %s" % user_profile.floor
    
  elif standings_group == "all":
    profiles = Profile.objects.all().order_by("-points", "-last_awarded_submission")
    title = "Individual standings, Everyone"
  else:
    raise StandingsException("Unknown standings type %s" % standings_type)
    
  info, user_index = _calculate_user_standings(user_profile, profiles)
  
  # Construct return dictionary.
  return json.dumps({
    "title": title,
    "info": info,
    "myindex": user_index,
    "type": standings_type,
  })
  
def _calculate_user_standings(user_profile, profiles):
  """Finds user standings based on the user's profile and a list of profiles.
  Returns dictionary of points and the index of the user."""
  
  # First and last users are easy enough to retrieve.
  first = profiles[0]
  profile_count = profiles.count()
  last = profiles[profile_count-1]
  
  # Search for user.
  rank = 1
  above_points = first.points
  below_points = last.points
  found_user = False
  for profile in profiles:
    if profile == user_profile:
      # Set flag that we found the user.
      found_user = True
    elif not found_user:
      # If we haven't found the user yet, keep going.
      above_points = profile.points
      rank += 1
    elif found_user:
      # If we found the user, then this is the person just after.
      below_points = profile.points
      break
      
  # Construct the return dictionary.
  index = 0
  info = [{"points": first.points, "rank": 1, "label": ''}]
  
  # Append above points
  if rank == 2:
    # There's no above points, since that is #1
    index = 1
  elif rank > 2:
    info.append({"points": above_points, "rank": rank - 1, "label": ''})
    index = 2
  
  # Append user points if they are not #1
  if rank > 1:
    info.append({"points": user_profile.points, "rank": rank, "label": ''})

  # Append below and/or last only if the user is not ranked last.
  if rank < profile_count:
    if rank < profile_count - 1:
      # Append the below points if the user is ranked higher than second to last.
      info.append({"points": below_points, "rank": rank + 1, "label": ''})
    info.append({"points": last.points, "rank": profile_count, "label": ''})
    
  return info, index
    
    
      
    
  
  