# Default string to use as the floor label.

DEFAULT_FLOOR_LABEL = "Floor"

def get_floor_label():
  """Returns the floor label from the settings or the default if it doesn't exist."""
  
  try:
    import competition_settings as settings
    
    if settings.COMPETITION_GROUP_NAME:
      floor_label = settings.COMPETITION_GROUP_NAME
    else:
      floor_label = DEFAULT_FLOOR_LABEL
  except ImportError:
    floor_label = DEFAULT_FLOOR_LABEL
    
  return floor_label