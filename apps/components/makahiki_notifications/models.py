import datetime

from django.db import models
from django.contrib.auth.models import User

NOTIFICATION_TYPES = (
    ("alert", "alert"),
    ("sticky", "sticky"),
    ("email", "email"),
    ("text_message", "text_message"),
)

class Notification(models.Model):
  recipient = models.ForeignKey(User)
  contents = models.TextField()
  processed_at = models.DateTimeField(null=True, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  level = models.IntegerField(default=0)
  notification_type = models.CharField(
      max_length=20,
      choices=NOTIFICATION_TYPES,
  )
  
  @staticmethod
  def process_alert_notifications(user):
    notifications = user.notification_set.filter(
        processed_at__isnull=True,
        notification_type="alert",
    )
    
    for notification in notifications:
      notification.processed_at = datetime.datetime.today()
      notification.save()
      
    return notifications
    
  @staticmethod
  def process_sticky_notifications(user):
    # Sticky notifications must be marked as read by the user.
    return user.notification_set.filter(
        processed_at__isnull=True,
        notification_type="sticky",
    )
    
  def mark_as_read(self):
    self.processed_at = datetime.datetime.today()
    self.save()
    
class Observable(models.Model):
  class Meta:
    abstract = True
    
  def create_notification(self):
    raise NotImplementedError("Subclasses must implement create_notification.")
    
  def save(self):
    super(Observable, self).save()
    self.create_notification()
    