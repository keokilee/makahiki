import datetime
from django.conf import settings

from django.shortcuts import render_to_response
from django.template import RequestContext

# Default string to use as the floor label.
DEFAULT_FLOOR_LABEL = "Floor"

def get_floor_label():
  """Returns the floor label from the settings or the default if it doesn't exist."""
  
  if settings.COMPETITION_GROUP_NAME:
    return settings.COMPETITION_GROUP_NAME
  else:
    return DEFAULT_FLOOR_LABEL
  
def get_round_info():
  """Returns a dictionary containing round information."""
  # Copy the round info and insert the overall round.
  rounds = settings.COMPETITION_ROUNDS.copy()
  rounds["Overall"] = {"start": settings.COMPETITION_START, "end": settings.COMPETITION_END}
  
  return rounds
  
def get_rounds_for_header():
  """Handles the round information that will be used to generate the header."""
  # Copy the round info and insert the overall round.
  rounds = get_round_info()
  
  # Calculate the number of days ago each of the rounds occurred in.
  return_dict = {}
  today = datetime.datetime.combine(datetime.date.today(), datetime.time())
  for key, value in rounds.items():
    start_date = datetime.datetime.strptime(value["start"], "%Y-%m-%d")
    end_date = datetime.datetime.strptime(value["end"], "%Y-%m-%d")
    start = (today - start_date).days
    end = (today - end_date).days + 1 # Round technically ends the day before.
      
    return_dict.update({
      key: {
        "start": start,
        "end": end,
      }
    })
  
  return return_dict
  
def get_current_round():
  """Gets the current round from the settings."""
  rounds = settings.COMPETITION_ROUNDS
  today = datetime.datetime.today()
  for key in rounds.keys():
    start = datetime.datetime.strptime(rounds[key]["start"], "%Y-%m-%d")
    end = datetime.datetime.strptime(rounds[key]["end"], "%Y-%m-%d")
    if today >= start and today < end:
      return key
    
  # No current round.
  return None
  
def get_current_round_info():
  """Gets the current round and associated dates."""
  rounds = settings.COMPETITION_ROUNDS
  today = datetime.datetime.today()
  for key in rounds.keys():
    start = datetime.datetime.strptime(rounds[key]["start"], "%Y-%m-%d")
    end = datetime.datetime.strptime(rounds[key]["end"], "%Y-%m-%d")
    if today >= start and today < end:
      return {
          "name": key,
          "start": start,
          "end": end,
      }
      
  # Check for overall round info.
  start = datetime.datetime.strptime(settings.COMPETITION_START, "%Y-%m-%d")
  end = datetime.datetime.strptime(settings.COMPETITION_END, "%Y-%m-%d")
  if today >= start and today < end:
    return {
        "name": "Overall",
        "start": start,
        "end": end,
    }
  
  # No current round.
  return None

def in_competition():
  """Returns true if we are still in the competition."""
  start = datetime.datetime.strptime(settings.COMPETITION_START, "%Y-%m-%d")
  end = datetime.datetime.strptime(settings.COMPETITION_END, "%Y-%m-%d")
  today = datetime.datetime.today()
  if today >= start and today < end:
    return True
  
  return False
    
def get_competition_dates():
  """Returns information about the competition."""
  start = datetime.datetime.strptime(settings.COMPETITION_START, "%Y-%m-%d")
  end = datetime.datetime.strptime(settings.COMPETITION_END, "%Y-%m-%d")
  
  return {
    "title": "Competition",
    "start": start,
    "end": end,
  }
  
def get_theme():
  """Get the current theme and returns the theme settings."""

  theme = settings.MAKAHIKI_THEME or "default"
  if settings.MAKAHIKI_THEME_SETTINGS.has_key(theme):
    return theme, settings.MAKAHIKI_THEME_SETTINGS[theme]
  elif settings.MAKAHIKI_THEME_SETTINGS.has_key("default"):
    return theme, settings.MAKAHIKI_THEME_SETTINGS["default"]
  else:
    return None, {}
    
def restricted(request, message=None):
  """Helper method to return a error message when a user accesses a page they are not allowed to view."""

  if not message:
    message = "You are not allowed to view this page."
    
  return render_to_response("restricted.html", {
    "message": message,
  }, context_instance = RequestContext(request))