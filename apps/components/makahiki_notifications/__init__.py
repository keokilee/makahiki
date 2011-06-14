import datetime

from components.makahiki_notifications.models import UserNotification

def get_unread_notifications(user, limit=None):
  """
  Retrieves the user's unread notifications that are to be displayed on the web.
  Returns a dictionary containing their alerts, their unread notifications, and if there are
  more unread notifications.
  """
  if not user:
    return None
    
  notifications = {"has_more": False}

  # Find undisplayed alert notifications.
  notifications.update({"alerts": get_user_alert_notifications(user)})

  # Get unread notifications
  unread_notifications = user.usernotification_set.filter(
      unread=True,
  ).order_by("-level", "-created_at")
  if limit:
    if unread_notifications.count() > limit:
      notifications.update({"has_more": True})
    unread_notifications = unread_notifications[:limit]

  notifications.update({"unread": unread_notifications})
  
  return notifications
  
def get_unread_count(user):
  """
  Get the number of notifications that are unread.
  """
  return UserNotification.objects.filter(recipient=user, unread=True).count()
  
def get_user_alert_notifications(user):
  """
  Retrieves notifications that should be displayed in an alert.  The notifications are
  then marked as displayed so that they don't display again.
  """
  notifications = user.usernotification_set.filter(
      unread=True,
      display_alert=True,
  ).order_by("-level", "-created_at")
    
  return notifications
  