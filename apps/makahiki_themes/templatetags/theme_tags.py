from django import template
from django.conf import settings

import os
import string

register = template.Library()

def render_css_import(user=None):
  """Renders the CSS import header statements for a template."""

  return_string = ""
  current_theme = settings.MAKAHIKI_THEME
    
  css_dir = os.path.join(settings.PROJECT_ROOT, "media", current_theme, "css")
  
  if os.path.isdir(css_dir):
    items = (item for item in os.listdir(css_dir) if string.find(item, "css") >= 0)
    for item in items:
      if item != "mobile.css":
        return_string += "<link rel=\"stylesheet\" href=\"/site_media/static/" + current_theme
        return_string += "/css/" + item + "\" />\n"
  
  return return_string

register.simple_tag(render_css_import)

def render_css_select(user=None):
  """Renders a dropdown select box for changing themes."""
  
  return_string = "<form action=\"/themes/change_theme/\" method=\"post\">"
  return_string += "CSS select: <select name=\"css_theme\" onchange=\"this.form.submit()\">"
  theme_dir = os.path.join(settings.PROJECT_ROOT, "media")
  
  items = (item for item in os.listdir(theme_dir) if os.path.isdir(os.path.join(theme_dir, item, "css")))
  current_theme = settings.MAKAHIKI_THEME
  
  for item in items:
    if item == current_theme:
      return_string += "<option selected=\"" + item + "\" value=\"" + item + "\">" + item + "</option>\n"
    else:
      return_string += "<option value=\"" + item + "\">" + item + "</option>\n"
  
  return_string += "</select></form>"
  return return_string
  
register.simple_tag(render_css_select)
