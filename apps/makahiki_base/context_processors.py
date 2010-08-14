DEFAULT_FLOOR_LABEL = "Floor"

def competition(request):
  """Provides access to standard competition constants within a template."""
  
  try:
    import competition_settings as settings
    
    if settings.COMPETITION_GROUP_NAME:
      floor_label = settings.COMPETITION_GROUP_NAME
    else:
      floor_label = DEFAULT_FLOOR_LABEL
  except ImportError:
    floor_label = DEFAULT_FLOOR_LABEL
    
  return {"floor_label": floor_label}