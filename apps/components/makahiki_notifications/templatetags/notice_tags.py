import sys

from django import template
from django.template import Library

register = Library()
  
@register.simple_tag
def mark_alerts_displayed(alerts):
  """
  Simple tag to mark the alerts displayed.
  """
  alerts.update(display_alert=False)
  return ""