import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib.messages import constants as message_constants

# Notification Levels
constants = message_constants

class Notification(models.Model):
  recipient = models.ForeignKey(User)
  contents = models.TextField()
  unread = models.BooleanField(default=True)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)
  level = models.IntegerField(default=constants.INFO)
  
  class Meta:
    abstract = True

class UserNotification(Notification):
  display_alert = models.BooleanField(default=False)
  
  @property
  def icon_class(self):
    if self.level == constants.ERROR:
      return "ui-icon-alert"
    elif self.level == constants.SUCCESS:
      return "ui-icon-star"
    return "ui-icon-info"
    
  @property
  def style_class(self):
    if self.level == constants.ERROR:
      return "ui-state-error"
      
    return "ui-state-highlight"
    
  @staticmethod
  def create_info_notification(recipient, contents, display_alert=False):
    notification = UserNotification(
        recipient=recipient,
        contents=contents,
        level=constants.INFO,
        display_alert=display_alert,
    )
    notification.save()
    
  @staticmethod
  def create_success_notification(recipient, contents, display_alert=False):
    notification = UserNotification(
        recipient=recipient,
        contents=contents,
        level=constants.SUCCESS,
        display_alert=display_alert,
    )
    notification.save()

  @staticmethod
  def create_warning_notification(recipient, contents, display_alert=True):
    notification = UserNotification(
        recipient=recipient,
        contents=contents,
        level=constants.WARNING,
        display_alert=display_alert,
    )
    notification.save()

  @staticmethod
  def create_error_notification(recipient, contents, display_alert=True):
    notification = UserNotification(
        recipient=recipient,
        contents=contents,
        level=constants.ERROR,
        display_alert=display_alert,
    )
    notification.save()
  
  
  
  

    