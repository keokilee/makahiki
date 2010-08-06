from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Sum, Max

from makahiki_profiles.models import Profile, ScoreboardEntry
from floors.models import Floor
import simplejson as json

# Default number of individuals to retrieve standings for when tracking across all dorms.
MAX_INDIVIDUAL_STANDINGS = 5

class StandingsException(Exception):
  def __init__(self, value):
    self.value = value
    
  def __str__(self):
    return repr(self.value)
    
def get_all_standings(dorm=None, grouping="floor", count=MAX_INDIVIDUAL_STANDINGS):
  """Retrieves standings across all floors for all rounds. Can be grouped by floor or by individual."""
  
  standings = []
  for round_name in settings.COMPETITION_ROUNDS.keys():
    if grouping == "floor":
      standings.append(get_floor_standings(dorm=dorm, round_name=round_name,))
    else:
      standings.append(get_individual_standings(dorm=dorm, round_name=round_name, count=count))
  
  # Append overall standings.
  if grouping == "floor":
    standings.append(get_floor_standings(dorm=dorm,))
  else:
    standings.append(get_individual_standings(dorm=dorm, count=count))
  
  return standings
  
def get_individual_standings(dorm=None, round_name=None, count=MAX_INDIVIDUAL_STANDINGS):
  """Retrieves standings across all floors for individual users."""
  title = "Floor vs. Floor: "
  # Build up the query set.
  profiles = Profile.objects
  if dorm:
    profiles = profiles.filter(floor__dorm=dorm)
    title = "%s: " % dorm.name
  
  if round_name:
    profiles = profiles.filter(scoreboardentry__round_name=round_name).annotate(
                points=Sum("scoreboardentry__points"),
                last_awarded_submission=Max("scoreboardentry__last_awarded_submission")
             ).order_by("-points", "-last_awarded_submission")[:count]
    title += round_name
  else:
    profiles = profiles.annotate(
                points=Sum("points"), 
                last_awarded_submission=Max("last_awarded_submission")
             ).order_by("-points", "-last_awarded_submission")[:count]
    title += "Overall"
             
  # Construct the standings info dictionary.
  info = []
  for i, profile in enumerate(profiles):
    info.append({
      "points": profile.points,
      "rank": i + 1,
      "label": profile.name,
    })
  
  return json.dumps({
    "title": title,
    "info": info,
  })
    
def get_floor_standings(dorm=None, round_name=None):
  """Retrieves standings across all floors grouped by floor."""
  
  title = "Floor vs. Floor: "
  # Build up the query set.
  floors = Floor.objects
  if dorm:
    floors = floors.filter(dorm=dorm)
    title = "%s: " % dorm.name
  
  if round_name:
    floors = floors.filter(profile__scoreboardentry__round_name=round_name).annotate(
                points=Sum("profile__scoreboardentry__points"),
                last_awarded_submission=Max("profile__scoreboardentry__last_awarded_submission")
             ).order_by("-points", "-last_awarded_submission")
    title += round_name
  else:
    floors = floors.annotate(
                points=Sum("profile__points"), 
                last_awarded_submission=Max("profile__last_awarded_submission")
             ).order_by("-points", "-last_awarded_submission")
    title += "Overall"
             
  # Construct the standings info dictionary.
  info = []
  for i, floor in enumerate(floors):
    info.append({
      "points": floor.points,
      "rank": i + 1,
      "label": floor.number,
    })
  
  return json.dumps({
    "title": title,
    "info": info,
  })
  
    
def get_all_standings_for_user(user, is_me=True, group="floor"):
  """Uses get_standings_for_user to generate standings for each round and the overall 
  standings for users in the user's floor.  Returns an array of the different standings."""
    
  standings = []
  for round_name in settings.COMPETITION_ROUNDS.keys():
    standings.append(get_standings_for_user(user, group=group, round_name=round_name, is_me=is_me))
  
  # Append overall standings.
  standings.append(get_standings_for_user(user, group=group, is_me=is_me))
  
  return standings
  
def get_standings_for_user(user, group="floor", round_name=None, is_me=True):
  """Generates standings for a user to be used in the standings widget.  
  Generates either floor-wide standings or standings based on all users.
  Returns a json structure for insertion into the javascript code."""
  
  standings_type = "individual"
  
  # Check for valid standings parameter.
  if group != "floor" and group != "all":
    raise StandingsException("Unknown standings type %s. Valid types are 'all' and 'floor'." % standings_type)
    
  user_profile = Profile.objects.get(user=user)
  
  if not user_profile.floor:
    # Nothing we can do again.
    raise StandingsException("User has no floor for standings.")
  
  title = user_entry = entries = None
  if round_name:
    # Calculate standings for round.
    user_entry = user_profile.scoreboardentry_set.get(round_name=round_name)
    
    if not settings.COMPETITION_ROUNDS or not settings.COMPETITION_ROUNDS.has_key(round_name):
      # Nothing we can do again.
      raise StandingsException("Unknown round name %s" % round_name)
    
    if group == "floor":
      entries = ScoreboardEntry.objects.filter(
                  profile__floor=user_profile.floor,
                  round_name=round_name,
                ).order_by("-points", "-last_awarded_submission")
      title = "Individual standings, %s, %s" % (user_profile.floor, round_name)
    else:
      entries = ScoreboardEntry.objects.filter(round_name=round_name).order_by("-points", "-last_awarded_submission")
      title = "Individual standings, Everyone, %s" % round_name
    
  else:
    # Calculate overall standings.
    user_entry = user_profile

    if group == "floor":
      entries = Profile.objects.filter(floor=user_profile.floor).order_by("-points", "-last_awarded_submission")
      title = "Individual standings, %s" % user_profile.floor

    else:
      entries = Profile.objects.all().order_by("-points", "-last_awarded_submission")
      title = "Individual standings, Everyone"

  
  info, user_index = _calculate_user_standings(user_entry, entries)
  
  # Construct JSON return dictionary.
  return json.dumps({
    "title": title,
    "info": info,
    "myindex": user_index,
    "type": standings_type,
  })
  
def _calculate_user_standings(user_entry, entries, round=None):
  """Finds user standings based on the user's entry and a list of entries.
  Note that this code works when the passed instances are Profiles or 
  ScoreboardEntries, since it only accesses the points field.
  
  Returns dictionary of points and the index of the user."""
  
  # First and last users are easy enough to retrieve.
  first = entries[0]
  entry_count = entries.count()
  last = entries[entry_count-1]
  
  # Search for user.
  rank = 1
  above_points = first.points
  below_points = last.points
  found_user = False
  for entry in entries:
    if entry == user_entry:
      # Set flag that we found the user.
      found_user = True
    elif not found_user:
      # If we haven't found the user yet, keep going.
      above_points = entry.points
      rank += 1
    elif found_user:
      # If we found the user, then this is the person just after.
      below_points = entry.points
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
    info.append({"points": user_entry.points, "rank": rank, "label": ''})

  # Append below and/or last only if the user is not ranked last.
  if rank < entry_count:
    if rank < entry_count - 1:
      # Append the below points if the user is ranked higher than second to last.
      info.append({"points": below_points, "rank": rank + 1, "label": ''})
    info.append({"points": last.points, "rank": entry_count, "label": ''})
    
  return info, index
    
    
      
    
  
  