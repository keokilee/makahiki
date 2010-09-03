from makahiki_base import get_floor_label

def competition(request):
  """Provides access to standard competition constants within a template."""
  
  return {"floor_label": get_floor_label()}