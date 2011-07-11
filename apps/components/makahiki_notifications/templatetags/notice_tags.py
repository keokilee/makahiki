import sys

from django import template
from django.template import Library

from components.logging import create_server_log

register = Library()
  
@register.simple_tag
def mark_alerts_displayed(request, alerts):
  """
  Simple tag to mark the alerts displayed.
  """
  for alert in alerts:
    create_server_log(request, "/slog/notifications/alert/%d/" % alert.pk)
    
  alerts.update(display_alert=False)
  return ""