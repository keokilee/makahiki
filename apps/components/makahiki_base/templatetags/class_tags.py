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
  theme_rules = sys.modules[theme_path]
  if theme_rules.RETURN_CLASSES: 
    return theme_rules.CSS_CLASSES[key]
    
  return ""
  
@register.simple_tag
def get_id_and_classes(key, theme="default"):
  """
  Outputs the id and class attributes for a tag.
  """
  theme_path = "css_rules.%s" % theme
  __import__(theme_path)
  theme_rules = sys.modules[theme_path]
  
  return_string = 'id="%s"' % key
  try:
    if theme_rules.RETURN_CLASSES and len(theme_rules.CSS_IDS[key]) > 0: 
      return return_string + ' class="%s"' % theme_rules.CSS_IDS[key]
      
  except KeyError:
    pass
    
  return return_string
  
@register.simple_tag
def import_css(static_url, theme="default"):
  """
  Returns HTML that imports CSS.  Typically should be used in the header section of a page.
  """
  theme_path = "css_rules.%s" % theme
  __import__(theme_path)
  theme_rules = sys.modules[theme_path]
  if theme_rules.RETURN_CLASSES: 
    return theme_rules.CSS_IMPORTS.format(static_url, theme)
    
  return ""
  
@register.simple_tag
def import_js(static_url, theme="default"):
  """
  Returns HTML that imports JS.  Typically should be used in the header section of a page.
  """
  theme_path = "css_rules.%s" % theme
  __import__(theme_path)
  theme_rules = sys.modules[theme_path]
  return theme_rules.JS_IMPORTS.format(static_url)
  # if theme_rules.RETURN_CLASSES: 
  #   return theme_rules.JS_IMPORTS.format(static_url)
  # 
  # return ""
  
@register.simple_tag
def import_page_css(page, static_url, theme="default"):
  """
  Returns HTML that imports CSS.  Typically should be used in the header section of a page.
  """
  theme_path = "css_rules.%s" % theme
  __import__(theme_path)
  theme_rules = sys.modules[theme_path]
  if theme_rules.RETURN_CLASSES: 
    return theme_rules.PAGE_CSS_IMPORT[page].format(static_url, theme)

  return ""
  
@register.simple_tag
def import_logged_in_css(static_url, theme="default"):
  """
  Returns HTML that imports CSS.  Typically should be used in the header section of a page with a logged in user.
  """
  theme_path = "css_rules.%s" % theme
  __import__(theme_path)
  theme_rules = sys.modules[theme_path]
  if theme_rules.RETURN_CLASSES: 
    return theme_rules.LOGGED_IN_CSS_IMPORT.format(static_url, theme)

  return ""