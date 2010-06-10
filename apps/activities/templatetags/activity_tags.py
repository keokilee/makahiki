from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
import datetime

from activities.models import Activity, Commitment, Goal, ActivityMember, CommitmentMember, GoalMember

register = template.Library()

def render_user_tools(user, item):
  """Renders the form used to add/remove activities and to request points."""
  
  if not isinstance(user, User):
    try:
      user = User.objects.get(username=user)
    except User.DoesNotExist():
      return ""
      
  if isinstance(item, Commitment):
    return __generate_commitment_form(user, item)
  elif isinstance(item, Activity):
    return __generate_activity_form(user, item)
  elif isinstance(item, Goal):
    return __generate_goal_form(user, item)
  else:
    return "";
  
register.simple_tag(render_user_tools)

# Private methods for constructing the form.
def __generate_commitment_form(user, item):
  # Check that the user is involved with this item.
  return_string = ""
  try:
    # Exception thrown if user cannot be found.
    item_join = CommitmentMember.objects.get(user=user, commitment=item, completed=False)
    
    if datetime.date.today() >= item_join.completion_date:
      return_string += '<a href="/activities/request_{0}_points/{1.id}">Request Points</a>&nbsp'
    else:
      diff = item_join.completion_date - datetime.date.today()
      return_string += '%d days left&nbsp' % diff.days
    
    return_string += '<form action="/activities/remove_{0}/{1.id}'
    return_string += '/" method="post" style="display:inline"><a href="#"'
    return_string += 'onclick="parentNode.submit()">Remove</a></form>'
  
  except ObjectDoesNotExist:
    return_string += '<form action="/activities/add_{0}/{1.id}'
    return_string += '/" method="post" style="display:inline">'
    return_string += '<a href="#" onclick="parentNode.submit()">Commit</a></form>'
    
  # return_string is a format string with places to insert the item type and item.
  return return_string.format("commitment", item)
  
def __generate_activity_form(user, item):
  """Generates the add/remove/request points links for the user."""
  # Check that the user is involved with this item.
  return_string = ""
  try:
    # Exception thrown if user cannot be found.
    item_join = ActivityMember.objects.get(user=user, activity=item)
    if item_join.approval_status == u"unapproved" or item_join.approval_status == u"rejected":
      return_string += '<a href="/activities/request_{0}_points/{1.id}/">I Did This!</a>&nbsp'
    elif item_join.approval_status == u"pending":
      return_string += "<span class=\"pending_activity\">Pending</span>&nbsp"
      
    # TODO What should happen if the points are rejected?
    if item_join.approval_status != u"approved":
      return_string += '<form action="/activities/remove_{0}/{1.id}'
      return_string += '/" method="post" style="display:inline"><a href="#"'
      return_string += 'onclick="parentNode.submit()">Remove</a></form>'
  
  except ObjectDoesNotExist:
    return_string += '<a href="/activities/request_{0}_points/{1.id}/">I Did This!</a>&nbsp'
    
    return_string += '<form action="/activities/add_{0}/{1.id}'
    return_string += '/" method="post" style="display:inline">'
    return_string += '<a href="#" onclick="parentNode.submit()">Like</a></form>'
    
  # return_string is a format string with places to insert the item type and item.
  return return_string.format("activity", item)
  
def __generate_goal_form(user, item):
  """Generates the add/remove/request points links for the user."""
  # Check that the user is involved with this item.
  return_string = ""
  try:
    # Exception thrown if user cannot be found.
    item_join = GoalMember.objects.get(floor=user.get_profile().floor, goal=item)
    if (item_join.approval_status == u"unapproved" or item_join.approval_status == u"rejected") and item_join.user == user:
      return_string += '<a href="/activities/request_{0}_points/{1.id}/">We Did This!</a>&nbsp'
      
    elif item_join.approval_status == u"pending":
      return_string += "<span class=\"pending_activity\">Pending</span>&nbsp"
      
    # TODO What should happen if the points are rejected?
    if item_join.approval_status != u"approved" and item_join.user == user:
      return_string += '<form action="/activities/remove_{0}/{1.id}'
      return_string += '/" method="post" style="display:inline"><a href="#"'
      return_string += 'onclick="parentNode.submit()">Remove</a></form>'
    else:
      return_string += "<span class=\"approved_activity\">Approved</span>"
  
  except ObjectDoesNotExist:
    if GoalMember.can_add_goal(user):
      return_string += '<form action="/activities/add_{0}/{1.id}'
      return_string += '/" method="post" style="display:inline">'
      return_string += '<a href="#" onclick="parentNode.submit()">Add</a></form>'
    else:
      return_string += "You cannot add more goals."
    
  # return_string is a format string with places to insert the item type and item.
  return return_string.format("goal", item)