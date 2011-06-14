import datetime
import random
import string
import os

from django.db import models, IntegrityError
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse

# Register badges immediately.
from components.makahiki_badges.user_badges import FullyCommittedBadge
from lib.brabeion import badges

badges.register(FullyCommittedBadge)

from components.floors.models import Post
from components.makahiki_base.models import Like
from components.makahiki_notifications.models import UserNotification

MARKDOWN_LINK = "http://daringfireball.net/projects/markdown/syntax"
MARKDOWN_TEXT = "Uses <a href=\"" + MARKDOWN_LINK + "\" target=\"_blank\">Markdown</a> formatting."
    
class Category(models.Model):
  """Categories used to group commitments and activities."""
  name = models.CharField(max_length=255, help_text="255 character maximum")
  slug = models.SlugField(help_text="Automatically generated if left blank.", null=True)

  class Meta:
    verbose_name_plural = "categories"

  def __unicode__(self):
    return self.name

class TextPromptQuestion(models.Model):
  """Represents questions that can be asked of users in order to verify participation in activities."""
  
  activity = models.ForeignKey("Activity")
  question = models.TextField()
  answer = models.CharField(max_length=255, help_text="255 character max.", null=True, blank=True)
  
  def __unicode__(self):
    return self.question

class QuestionChoice(models.Model):
  """Represents questions's multiple choice"""
  
  question = models.ForeignKey("TextPromptQuestion")
  activity = models.ForeignKey("Activity")
  choice = models.CharField(max_length=255, help_text="255 character max.")
  
  def __unicode__(self):
    return self.choice
    
class ConfirmationCode(models.Model):
  """Represents confirmation codes for activities."""
  activity = models.ForeignKey("Activity")
  code = models.CharField(max_length=10, unique=True)
  is_active = models.BooleanField(default=True, editable=False)
  
  @staticmethod
  def generate_codes_for_activity(activity, num_codes):
    """Generates a set of random codes for the activity."""
    
    values = 'abcdefghijklmnopqrstuvwxyz0123456789'
    # Use the first 4 characters of the activity title as the start of the code.
    header = string.join(activity.title.split(), "")
    header = header.lower()[:4]
    header += "-"
    for i in range(0, num_codes):
      code = ConfirmationCode(activity=activity, code=header)
      valid = False
      while not valid:
        for value in random.sample(values, 5):
          code.code += value
        try:
          # print code.code
          # Throws exception if the code is a duplicate.
          code.save()
          valid = True
        except IntegrityError:
          # Try again.
          code.code = header
          
# ActivityBase 
class ActivityBase(models.Model):
  TYPE_CHOICES = (
    ('activity', 'Activity'),
    ('commitment', 'Commitment'),
    ('event', 'Event'),
    ('survey', 'Survey'),
    ('excursion', 'Excursion'),
  )
  
  name = models.CharField(max_length=20, null=True)
  slug = models.SlugField(help_text="Automatically generated if left blank.", null=True)
  title = models.CharField(max_length=200)
  description = models.TextField(help_text=MARKDOWN_TEXT)
  type = models.CharField(
                  max_length=20, 
                  choices=TYPE_CHOICES, 
                  verbose_name="Activity Type"
                 )
  category = models.ForeignKey(Category, null=True)
  priority = models.IntegerField(
                default=1000,
                help_text="Orders the activities in the available activities list. " + 
                          "Activities with lower values (higher priority) will be listed first."
             )
  likes = generic.GenericRelation(Like)
  depends_on = models.CharField(max_length=400, null=True, blank=True,)
  depends_on_text = models.CharField(max_length=400, null=True, blank=True,)
  energy_related = models.BooleanField(default=False)
  
  created_at = models.DateTimeField(editable=False, auto_now_add=True)
  updated_at = models.DateTimeField(editable=False, auto_now=True, null=True)
    
class Commitment(ActivityBase):
  """Commitments involve non-verifiable actions that a user can commit to.
  Typically, they will be worth fewer points than activities."""
  duration = models.IntegerField(default=5, help_text="Duration of commitment, in days.")
  point_value = models.IntegerField(
                  help_text="Specify a single point value to be awarded."
                ) # This is validated by the admin form.  
  users = models.ManyToManyField(User, through="CommitmentMember")
  
  def __unicode__(self):
    return self.title
    
class Activity(ActivityBase):
  """Activities involve verifiable actions that users commit to.  These actions can be 
  verified by asking questions or posting an image attachment that verifies the user did 
  the activity."""
  
  class Meta:
    verbose_name_plural = "activities"
  
  CONFIRM_CHOICES = (
    ('text', 'Question and Answer'),
    ('image', 'Image Upload'),
    ('code', 'Confirmation Code'),
    ('free', 'Free Response'),
  )
  
  users = models.ManyToManyField(User, through="ActivityMember")
  duration = models.IntegerField(
              verbose_name="Expected activity duration",
              help_text="Time (in minutes) that the activity is expected to take."
             )
  point_value = models.IntegerField(
                  null=True, 
                  blank=True, 
                  help_text="Specify a single point value or a range of points to be awarded."
                ) # This is validated by the admin form.               
  point_range_start = models.IntegerField(
                        null=True, 
                        blank=True, 
                        help_text="Minimum number of points possible for this activity."
                      )
  point_range_end = models.IntegerField(
                        null=True, 
                        blank=True, 
                        help_text="Maximum number of points possible for this activity."
                      )
  
  pub_date = models.DateField(
              default=datetime.date.today(),
              verbose_name="Publication date",
              help_text="Date at which the activity will be available for users."
             )
  expire_date = models.DateField(
                verbose_name="Expiration date", 
                help_text="Date at which the activity will be removed."
              )
  confirm_type = models.CharField(
                  max_length=20, 
                  choices=CONFIRM_CHOICES, 
                  default="text",
                  verbose_name="Confirmation Type"
                 )
  confirm_prompt = models.TextField(
                    blank=True, 
                    verbose_name="Confirmation prompt",
                    help_text="Text to display to user when requesting points (for images, free response, and codes)."
                   )
  event_date = models.DateTimeField(
                null=True, 
                blank=True, 
                verbose_name="Date and time of the event",
                help_text="Required for events."
               )
  event_location = models.CharField(
                    blank=True,
                    null=True,
                    max_length=200, 
                    verbose_name="Event Location",
                    help_text="Location of the event"
                )
                      
  def __unicode__(self):
    return self.title
    
  def _is_active(self):
    """Determines if the activity is available for users to participate."""
    return self.is_active_for_date(datetime.date.today())
    
  is_active = property(_is_active)
  
  def is_active_for_date(self, date):
    """Determines if the activity is available for user participation at the given date."""
    pub_result = date - self.pub_date
    expire_result = self.expire_date - date
    if pub_result.days < 0 or expire_result.days < 0:
      return False
    return True
  
  def is_event_completed(self):
    """Determines if the event is completed."""
    result = datetime.datetime.today() - self.event_date
    if result.days >= 0 and result.seconds >= 0:
      return True
    return False
    
  def _has_variable_points(self):
    """Returns true if the activity uses variable points, false otherwise."""
    if self.point_value > 0:
      return False
    else:
      return True
      
  has_variable_points = property(_has_variable_points)
  
  def liked_users(self):
    """Returns an array of users that like this activity."""
    return [like.user for like in self.likes.all()]
  
  def pick_question(self, user_id):
    """Choose a random question to present to a user."""
    if self.confirm_type != "text":
      return None
      
    questions = TextPromptQuestion.objects.filter(activity=self)
    if questions:
      return questions[user_id % len(questions)]
    else:
      return None

# These models represent the different types of activities users can commit to.
class CommonBase(models.Model):
  """Common fields to all models in this file."""
  
  created_at = models.DateTimeField(editable=False, auto_now_add=True)
  updated_at = models.DateTimeField(editable=False, auto_now=True, null=True)
    
  class Meta:
    abstract = True
    
class CommonActivityUser(CommonBase):
  """Common fields for items that need to be approved by an administrator."""
  
  STATUS_TYPES = (
    ('pending', 'Pending approval'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
  )
  
  approval_status = models.CharField(max_length=20, choices=STATUS_TYPES, default="pending")
  award_date = models.DateTimeField(null=True, blank=True, editable=False)
  submission_date = models.DateTimeField(null=True, blank=True, editable=False)

class CommitmentMember(CommonBase):
  """Represents the join between commitments and users.  Has fields for 
  commenting on a commitment and whether or not the commitment is currently 
  active."""
  
  user = models.ForeignKey(User)
  commitment = models.ForeignKey(Commitment)
  completion_date = models.DateField()
  award_date = models.DateTimeField(blank=True, null=True)
  comment = models.TextField(blank=True)
  
  def __unicode__(self):
    return "%s : %s" % (self.commitment.title, self.user.username)
    
  def days_left(self):
    """
    Returns how many days are left before the user can submit the activity.
    """
    diff = self.completion_date - datetime.date.today()
    if diff.days < 0:
      return 0
    
    return diff.days
  
  def save(self):
    """Custom save method to set fields depending on whether or not the item is just added or if the item is completed."""
    profile = self.user.get_profile()
    
    if not self.completion_date:
      self.completion_date = datetime.date.today() + datetime.timedelta(days=self.commitment.duration)
      
    if not self.pk and profile.floor:
      # User is adding the commitment.
      message = "is participating in the commitment \"%s\"." % (
        self.commitment.title,
      )
      post = Post(user=self.user, floor=profile.floor, text=message, style_class="system_post")
      post.save()
      
    if self.award_date:
      # User has finished the commitment.
      # Award the points
      profile = self.user.get_profile()
      profile.add_points(self.commitment.point_value, self.award_date)
      profile.save()
      
      if profile.floor:
        # Construct the points
        message = "has completed the commitment \"%s\"." % (
          self.commitment.title,
        )

        post = Post(user=self.user, floor=self.user.get_profile().floor, text=message, style_class="system_post")
        post.save()
        
    super(CommitmentMember, self).save()
    
    # Note, possibly_award is here because the member needs to be saved.
    badges.possibly_award_badge("fully_committed", user=self.user)
    
  def delete(self):
    """Custom delete method to remove the points for completed commitments."""
    profile = self.user.get_profile()
    
    if self.award_date:
      profile.remove_points(self.commitment.point_value, self.award_date)
      profile.save()
    elif profile.floor:
      message = "is no longer participating in \"%s\"." % (
        self.commitment.title,
      )
      post = Post(user=self.user, floor=self.user.get_profile().floor, text=message, style_class="system_post")
      post.save()
      
    super(CommitmentMember, self).delete()
  

def activity_image_file_path(instance=None, filename=None, user=None):
  """Returns the file path used to save an activity confirmation image."""
  
  from components.activities import ACTIVITY_FILE_DIR
  
  if instance:
    user = user or instance.user
  return os.path.join(ACTIVITY_FILE_DIR, user.username, filename)
                    
class ActivityMember(CommonActivityUser):
  """Represents the join between users and activities."""
  
  user = models.ForeignKey(User)
  activity = models.ForeignKey(Activity)
  question = models.ForeignKey(TextPromptQuestion, null=True, blank=True)
  response = models.CharField(blank=True, max_length=255, help_text="255 character max.")
  admin_comment = models.TextField(blank=True, help_text="Reason for approval/rejection")
  user_comment = models.TextField(blank=True, help_text="Comment from user about their submission.")
  image = models.ImageField(max_length=1024, 
                            blank=True, 
                            upload_to=activity_image_file_path,
                            help_text="Uploaded image for verification."
  )
  points_awarded = models.IntegerField(
      blank=True, 
      null=True, 
      help_text="Number of points to award for activities with variable point values."
  )
  
  def __unicode__(self):
    return "%s : %s" % (self.activity.title, self.user.username)
  
  def save(self, *args, **kwargs):
    """Custom save method to award/remove points if the activitymember is approved or rejected."""
    if self.approval_status == u"pending":
      # Mark pending items as submitted.
      self.submission_date = datetime.datetime.today()
      
    elif self.approval_status == u"approved" and not self.award_date:
      # Award users points and update wall.
      self.award_date = datetime.datetime.today()
      
      # Determine how many points to award.
      if self.activity.has_variable_points:
        points = self.points_awarded
      else:
        points = self.activity.point_value
        
      if not self.submission_date:
        # This may happen if it is an item with a confirmation code.
        self.submission_date = self.award_date
      profile = self.user.get_profile()
      profile.add_points(points, self.submission_date)
      profile.save()
      
      if profile.floor:
        # Post on the user's floor wall.
        message = " has been awarded %d points for completing \"%s\"." % (
          points,
          self.activity.title,
        )
        post = Post(user=self.user, floor=profile.floor, text=message, style_class="system_post")
        post.save()
      
    elif self.approval_status != u"approved" and self.award_date:
      # Removing user points and resetting award date.
      # Determine how many points to remove.
      if self.activity.has_variable_points:
        points = self.points_awarded
      else:
        points = self.activity.point_value
        
      profile = self.user.get_profile()
      profile.remove_points(points, self.submission_date)
      profile.save()
      self.award_date = None
      self.submission_date = None # User will have to resubmit.
      
    super(ActivityMember, self).save()
    
    # We check here for a rejected item because it should have an id now.
    if self.approval_status == u"rejected":
      # Construct the message to be sent.
      message = "Your response to <a href='%s'>%s</a> was not approved." % (
          reverse("activity_task", args=(self.activity.id,)),
          self.activity.title
      )
      
      message += " Please check your <a href='%s'>profile</a> for more information." % (
          reverse("profile_rejected", args=(self.id,)),
      )
      
      UserNotification.create_error_notification(self.user, message)
    
  def delete(self):
    """Custom delete method to remove awarded points."""
    
    if self.approval_status == u"approved":
      # Determine how many points to award.
      if self.activity.has_variable_points:
        points = self.points_awarded
      else:
        points = self.activity.point_value
        
      profile = self.user.get_profile()
      profile.remove_points(points, self.submission_date)
      profile.save()
      
    super(ActivityMember, self).delete()
