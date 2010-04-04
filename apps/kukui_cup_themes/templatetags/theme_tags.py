from django import template
from django.conf import settings

import os
import string

register = template.Library()

def render_css_import():
  """Renders the CSS import header statements for a template."""

  return_string = ""
  css_dir = os.path.join(settings.PROJECT_ROOT, "media", settings.KUKUI_CSS_THEME, "css")
  if os.path.isdir(css_dir):
    items = (item for item in os.listdir(css_dir) if string.find(item, "css") >= 0)
    for item in items:
        return_string += "<link rel=\"stylesheet\" href=\"/site_media/static/css/" + item + "\" />\n"
  
  return return_string

register.simple_tag(render_css_import)

