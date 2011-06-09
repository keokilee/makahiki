import datetime

from components.makahiki_notifications.models import UserNotification

def get_unread_notifications(user, limit=None):
  """
  Retrieves the user's unread notifications that are to be displayed on the web.
  Returns a dictionary containing their alerts and their regular notifications.
  """
  if not user:
    return None
    
  notifications = {}

  # Find undisplayed alert notifications.
  notifications.update({"alerts": get_user_alert_notifications(user)})

  # Get unread notifications
  unread_notifications = UserNotification.objects.filter(
      recipient=user,
      unread=True,
  ).order_by("-created_at")
  if limit:
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
  Retrieves notifications that should be displayed in an alert.  These notifications are
  automatically marked as read so that they don't appear again.
  """
  notifications = UserNotification.objects.filter(
      recipient=user,
      display_alert=True,
  ).order_by("-created_at")
  
  # Make sure these alerts are not displayed again.
  for notification in notifications:
    display_alert = False
    notification.save()
    
  return notifications
  