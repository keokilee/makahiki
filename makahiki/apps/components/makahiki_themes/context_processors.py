import simplejson as json
from django.conf import settings

from components.makahiki_themes.forms import ThemeSelect

def css_selector(request):
  """Provides the template with information about the currently selected CSS folder."""
  css_theme = settings.MAKAHIKI_THEME
  
  # Check if we are using the CSS selector and that the user selected a theme.
  if settings.ENABLE_CSS_SELECTOR and request.session.get("css_theme"):
    css_theme = request.session.get("css_theme")
    
  return {
    "ENABLE_CSS_SELECTOR": settings.ENABLE_CSS_SELECTOR, 
    "CSS_SELECT_FORM": ThemeSelect({"css_theme": css_theme}),
    "CSS_THEME": css_theme,
  }
