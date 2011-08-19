import sys
from datetime import datetime

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

MOMENT = 120    # duration in seconds within which the time difference 
                # will be rendered as 'a moment ago'

@register.filter
def naturalTimeDifference(value):
    """
    Finds the difference between the datetime value given and now
    and returns appropriate humanize form.  Found at:
    http://anandnalya.com/2009/05/20/humanizing-the-time-difference-in-django/

    Note that the naturaltime filter will be in Django 1.4, so this won't be necessary then.
    """
    if isinstance(value, datetime):
        delta = datetime.now() - value
        if delta.days > 6:
            return value.strftime("%b %d")                    # May 15
        if delta.days > 1:
            return value.strftime("%A")                       # Wednesday
        elif delta.days == 1:
            return 'yesterday'                                # yesterday
        elif delta.seconds >= 7200:
            return str(delta.seconds / 3600 ) + ' hours ago'  # 3 hours ago
        elif delta.seconds >= 3600:
            return '1 hour ago'                               # 1 hour ago
        elif delta.seconds >  MOMENT:
            return str(delta.seconds/60) + ' minutes ago'     # 29 minutes ago
        else:
            return 'a moment ago'                             # a moment ago
        return defaultfilters.date(value)
    else:
        return str(value)