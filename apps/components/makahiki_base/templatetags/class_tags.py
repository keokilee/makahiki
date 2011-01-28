import sys

from django import template
from django.template import Library

register = Library()

@register.simple_tag
def insert_classes(key, theme="default"):
  """
  Provides a string of classes that are assigned to the key.
  """
  # Import the theme dynamically from the passed in theme value.
  # Solution found at http://docs.python.org/library/functions.html#__import__
  theme_path = "css_rules.%s" % theme
  __import__(theme_path)
  theme = sys.modules[theme_path]
  if theme.RETURN_CLASSES: 
    return theme.CSS_CLASSES[key]
    
  return ""
  
@register.simple_tag
def get_id_and_classes(key, theme="default"):
  """
  Outputs the id and class attributes for a tag.
  """
  theme_path = "css_rules.%s" % theme
  __import__(theme_path)
  theme = sys.modules[theme_path]
  
  return_string = 'id="%s"' % key
  if theme.RETURN_CLASSES: 
    return return_string + ' class="%s"' % theme.CSS_IDS[key]
    
  return return_string