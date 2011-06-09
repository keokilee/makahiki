import datetime

from django.db import models
from django.contrib.auth.models import User

STYLE_CLASSES = (
    ("notification-info", "INFO"),
    ("notification-error", "ERROR"),
    ("notification-success", "SUCCESS"),
)

class UserNotification(models.Model):
  recipient = models.ForeignKey(User)
  contents = models.TextField()
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)
  display_alert = models.BooleanField(default=False)
  unread = models.BooleanField(default=True)
  style_class = models.CharField(
      max_length=20, 
      default="notification-info", 
      choices=STYLE_CLASSES
  )

    