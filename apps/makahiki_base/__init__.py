import competition_settings as settings

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
  rounds = settings.COMPETITION_ROUNDS
  rounds.update({"Competition": {"start": settings.COMPETITION_START, "end": settings.COMPETITION_END}})
  
  return rounds