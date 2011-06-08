import datetime

from django.db import models
from django.contrib.auth.models import User

NOTIFICATION_TYPES = (
    ("alert", "alert"),
    ("sticky", "sticky"),
    ("email", "email"),
    ("text_message", "text_message"),
)

STYLE_CLASSES = (
    ("notification-info", "INFO"),
    ("notification-error", "ERROR"),
    ("notification-success", "SUCCESS"),
)

class Notification(models.Model):
  recipient = models.ForeignKey(User)
  contents = models.TextField()
  read_at = models.DateTimeField(null=True, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  style_class = models.CharField(
      max_length=20, 
      default="notification-info", 
      choices=STYLE_CLASSES
  )
  notification_type = models.CharField(
      max_length=20,
      choices=NOTIFICATION_TYPES,
  )

    