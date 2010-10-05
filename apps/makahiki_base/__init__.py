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
  rounds = settings.COMPETITION_ROUNDS.copy()
  rounds["Competition"] = {"start": settings.COMPETITION_START, "end": settings.COMPETITION_END}
  
  return rounds
  
def get_current_round():
  """Gets the current round from the settings."""
  rounds = settings.COMPETITION_ROUNDS
  today = datetime.datetime.today()
  for index, key in enumerate(rounds.keys()):
    start = datetime.datetime.strptime(rounds[key]["start"], "%Y-%m-%d")
    end = datetime.datetime.strptime(rounds[key]["end"], "%Y-%m-%d")
    if today >= start and today < end:
      return {
        "title": key,
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
    return settings.MAKAHIKI_THEME_SETTINGS[theme]
  elif settings.MAKAHIKI_THEME_SETTINGS.has_key("default"):
    return settings.MAKAHIKI_THEME_SETTINGS["default"]
  else:
    return {}
    
def restricted(request, message=None):
  """Helper method to return a error message when a user accesses a page they are not allowed to view."""

  if not message:
    message = "You are not allowed to view this page."
    
  return render_to_response("restricted.html", {
    "message": message,
  }, context_instance = RequestContext(request))