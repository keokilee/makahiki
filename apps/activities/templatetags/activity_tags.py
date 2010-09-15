from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
import datetime

from activities.models import Activity, Commitment, ActivityMember, CommitmentMember

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
  else:
    return "";
  
register.simple_tag(render_user_tools)

# Private methods for constructing the form.
def __generate_commitment_form(user, item):
  # Check that the user is involved with this item.
  return_string = ""
  try:
    # Exception thrown if user cannot be found.
    item_join = CommitmentMember.objects.get(user=user, commitment=item, award_date__isnull=True)
    
    if datetime.date.today() >= item_join.completion_date:
      return_string += '<a href="/activities/request_{0}_points/{1.id}" '
      return_string += 'class="option-link ui-state-default ui-corner-all ui-state-hover">'
      return_string += '<span class="ui-icon ui-icon-circle-check"></span>'
      return_string += '<span class="button-text">I Did This!</span></a>'
    else:
      diff = item_join.completion_date - datetime.date.today()
      return_string += '%d days left ' % diff.days
    
    return_string += '<form action="/activities/remove_{0}/{1.id}/" method="post" onsubmit="">'
    return_string += '<a href="#" onclick="confirm_removal(parentNode, \'commitment\')" class="option-link ui-state-error ui-corner-all ui-state-hover">'
    return_string += '<span class="ui-icon ui-icon-circle-minus"></span><span class="button-text">Remove</span></a></form>'
  
  except ObjectDoesNotExist:
    return_string += '<form action="/activities/add_{0}/{1.id}'
    return_string += '/" method="post">'
    return_string += '<a href="#" onclick="parentNode.submit()" class="option-link ui-state-default ui-corner-all ui-state-hover">'
    return_string += '<span class="ui-icon ui-icon-circle-plus"></span><span class="button-text">Commit</span></a></form>'
    
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
      return_string += '<a href="/activities/request_{0}_points/{1.id}/" '
      return_string += 'class="option-link ui-state-default ui-corner-all ui-state-hover">'
      return_string += '<span class="ui-icon ui-icon-circle-check"></span>'
      return_string += '<span class="button-text">I Did This!</span></a> '
    elif item_join.approval_status == u"pending":
      return_string += "<span class=\"pending_activity\">Submitted for approval</span> "
      
    # TODO What should happen if the points are rejected?
    if item_join.approval_status != u"approved":
      return_string += '<form action="/activities/remove_{0}/{1.id}/" method="post">'
      return_string += '<a href="#" onclick="confirm_removal(parentNode, \'activity\')" class="option-link ui-state-error ui-corner-all ui-state-hover">'
      return_string += '<span class="ui-icon ui-icon-circle-minus"></span><span class="button-text">Remove</span></a></form>'
  
  except ObjectDoesNotExist:
    return_string += '<a href="/activities/request_{0}_points/{1.id}/" '
    return_string += 'class="option-link ui-state-default ui-corner-all ui-state-hover">'
    return_string += '<span class="ui-icon ui-icon-circle-check"></span>'
    return_string += '<span class="button-text">I Did This!</span></a>'
    
    # try:
    #   content_type = ContentType.objects.get(app_label="activities", model="Activity")
    #   like = Like.objects.get(user=user, object_type=content_type, object_id=item.id)
    #   # No exception thrown, so the user likes the activity
    #   return_string += '<h5 style="padding: 0; margin: 0">You like this activity.</h5>'
    # except ObjectDoesNotExist:
    #   return_string += '<form action="/activities/like_{0}/{1.id}/" method="post">'
    #   return_string += '<a href="#" onclick="parentNode.submit()">Like</a></form>'
    
  # return_string is a format string with places to insert the item type and item.
  return return_string.format("activity", item)
