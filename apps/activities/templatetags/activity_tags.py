from django import template
from django.contrib.auth.models import User

from activities.models import Activity, Commitment, Goal

register = template.Library()

def render_user_tools(user, item):
  """Renders the form used to add/remove activities and to request points."""
  
  if not isinstance(user, User):
    try:
      user = User.objects.get(username=user)
    except User.DoesNotExist():
      return ""
      
  if isinstance(item, Commitment):
    item_type = "commitment"
  elif isinstance(item, Activity):
    item_type = "activity"
  else:
    return "";
  
  # Check that the user is involved with this item.
  return_string = ""
  try:
    item.users.get(username=user.username)
    
    if isinstance(item, Activity):
      return_string += '<form action="/activities/request_{0}_points/{1.id}'
      return_string += '/" method="post" style="display:inline"><a href="#"'
      return_string += 'onclick="parentNode.submit()">Request Points</a></form>&nbsp'
    
    return_string += '<form action="/activities/remove_{0}/{1.id}'
    return_string += '/" method="post" style="display:inline"><a href="#"'
    return_string += 'onclick="parentNode.submit()">Remove</a></form>'
  
  except User.DoesNotExist:
    return_string += '<form action="/activities/add_{0}/{1.id}'
    return_string += '/" method="post" style="display:inline">'
    return_string += '<a href="#" onclick="parentNode.submit()">Add</a></form>'
    
  # return_string is a format string with places to insert the item type and item.
  return return_string.format(item_type, item)
  
register.simple_tag(render_user_tools)