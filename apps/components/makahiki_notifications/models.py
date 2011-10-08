import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib.messages import constants as message_constants
from django.core.mail.message import EmailMultiAlternatives
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.template import Template, Context
from markdown import markdown

# Notification Levels
constants = message_constants

TYPE_CHOICES = (
  ('round-transition', 'Round Transition'),
  ('raffle-winner', 'Raffle Winner'),
  ('canopy-elevation', 'Canopy Elevation'),
  ('commitment-ready', 'Commitment Ready'),
)

class NoticeTemplate(models.Model):
  """
  Templates for built in notifications.
  """
  TEMPLATE_TEXT = """
  Uses <a href='http://daringfireball.net/projects/markdown/syntax'>Markdown</a> formatting. 
  The available template variables are listed 
  <a href='https://github.com/keokilee/makahiki/wiki/Notice-Templates'>here</a>.
  """
  notice_type = models.SlugField(max_length=50, choices=TYPE_CHOICES)
  template = models.TextField(help_text=TEMPLATE_TEXT)
    
  def render(self, context_dict={}):
    """
    Renders the message first using Django's templating system, then using Markdown.
    The template renderer uses the passed in context to insert variables.
    """
    template = Template(self.template)
    template = template.render(Context(context_dict))
      
    return markdown(template)
    
  def __unicode__(self):
    return self.notice_type

class UserNotification(models.Model):
  recipient = models.ForeignKey(User)
  contents = models.TextField()
  unread = models.BooleanField(default=True)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)
  level = models.IntegerField(default=constants.INFO)
  
  display_alert = models.BooleanField(default=False)
  content_type = models.ForeignKey(ContentType, null=True, blank=True)
  object_id = models.PositiveIntegerField(null=True, blank=True)
  content_object = generic.GenericForeignKey('content_type', 'object_id')
  
  @property
  def is_success(self):
    if self.level == constants.SUCCESS:
      return True
    
    return False
    
  @property
  def icon_class(self):
    if self.level == constants.ERROR:
      return "ui-icon-alert"
    elif self.level == constants.SUCCESS:
      return "ui-icon-star"
      
    return "ui-icon-info"
    
  @property
  def style_class(self):
    if self.level == constants.ERROR or self.level == constants.WARNING:
      return "ui-state-error"
      
    return "ui-state-highlight"
    
  @staticmethod
  def create_info_notification(recipient, contents, display_alert=False, content_object=None):
    notification = UserNotification(
        recipient=recipient,
        contents=contents,
        level=constants.INFO,
        display_alert=display_alert,
    )
    if content_object:
      notification.content_object = content_object
      
    notification.save()
    
  @staticmethod
  def create_success_notification(recipient, contents, display_alert=False, content_object=None):
    notification = UserNotification(
        recipient=recipient,
        contents=contents,
        level=constants.SUCCESS,
        display_alert=display_alert,
    )
    if content_object:
      notification.content_object = content_object
      
    notification.save()

  @staticmethod
  def create_warning_notification(recipient, contents, display_alert=True, content_object=None):
    notification = UserNotification(
        recipient=recipient,
        contents=contents,
        level=constants.WARNING,
        display_alert=display_alert,
    )
    if content_object:
      notification.content_object = content_object
      
    notification.save()

  @staticmethod
  def create_error_notification(recipient, contents, display_alert=True, content_object=None):
    notification = UserNotification(
        recipient=recipient,
        contents=contents,
        level=constants.ERROR,
        display_alert=display_alert,
    )
    if content_object:
      notification.content_object = content_object
      
    # print display_alert
    notification.save()
    
  @staticmethod
  def create_email_notification(recipient_email, subject, message, html_message=None):
    msg = EmailMultiAlternatives(subject, message, settings.SERVER_EMAIL, [recipient_email,])
    if html_message:
      msg.attach_alternative(html_message, "text/html")
      
    msg.send()
    
  

    