import datetime
import random
import string
import os

from django.db import models, IntegrityError
from django.contrib.auth.models import User
from kukui_cup_profile.models import Profile
from tribes.models import Tribe

from activities import ACTIVITY_FILE_DIR

# These models represent the different types of activities users can commit to.

class CommonBase(models.Model):
  """Common fields to all models in this file."""
  
  created_at = models.DateTimeField(editable=False)
  updated_at = models.DateTimeField(null=True, editable=False)
  
  def save(self):
    if not self.id:
      self.created_at = datetime.datetime.today()
    else:
      self.updated_at = datetime.datetime.today()
    super(CommonBase, self).save()
    
  class Meta:
    abstract = True
    
class CommonActivityUser(CommonBase):
  """Common fields for items that need to be approved by an administrator."""
  
  STATUS_TYPES = (
    ('unapproved', 'Unapproved'),
    ('pending', 'Pending approval'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
  )
  
  approval_status = models.CharField(max_length=20, choices=STATUS_TYPES, default="unapproved")
  awarded = models.BooleanField(default=False, editable=False)

class CommonActivity(CommonBase):
  """Common fields for activity models."""
  
  title = models.CharField(max_length=200)
  description = models.TextField(help_text="Uses <a href=\"http://daringfireball.net/projects/markdown/\" target=\"_blank\">Markdown</a> formatting.")
  point_value = models.IntegerField()
  
  def __unicode__(self):
    return self.title
    
  class Meta:
    abstract = True

class Commitment(CommonActivity):
  """Commitments involve non-verifiable actions that a user can commit to.
  Typically, they will be worth fewer points than activities."""
  
  users = models.ManyToManyField(User, through="CommitmentMember")
  duration = models.IntegerField(default=5, help_text="Duration of commitment, in days.")
  
  def get_available_for_user(self, user):
    """Filter out commitments the user is currently active in."""
    commitments = Commitment.objects.exclude(
      commitmentmember__user__username=user.username,
      commitmentmember__is_active=True,
    )
    
    return commitments
    
class CommitmentMember(CommonBase):
  """Represents the join between commitments and users.  Has fields for 
  commenting on a commitment and whether or not the commitment is currently 
  active."""
  
  user = models.ForeignKey(User)
  commitment = models.ForeignKey(Commitment)
  completed = models.BooleanField(default=False)
  completion_date = models.DateField()
  comment = models.TextField(blank=True)
  
  def __unicode__(self):
    return "%s : %s" % (self.commitment.title, self.user.username)
  
  def save(self):
    """Custom save method to generate the completion date automatically."""
    if not self.completion_date:
      self.completion_date = datetime.date.today + timedelta(days=self.commitment.duration)
    
    super(CommitmentMember, self).save()
  
  def delete(self):
    """Custom delete method to remove the points for completed commitments."""
    if completed:
      profile = self.user.get_profile()
      profile.points -= self.commitment.point_value
      profile.save()
      
    super(CommitmentMember, self).delete()
  
class TextPromptQuestion(models.Model):
  """Represents questions that can be asked of users in order to verify participation in activities."""
  
  activity = models.ForeignKey("Activity")
  question = models.CharField(max_length=255, help_text="255 character max.")
  answer = models.CharField(max_length=255, help_text="255 character max.")
  
  def __unicode__(self):
    return self.question
    
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
          # Throws exception if the code is a duplicate.
          code.save()
          valid = True
        except IntegrityError:
          # Try again.
          code.code = header
      
class Activity(CommonActivity):
  """Activities involve verifiable actions that users commit to.  These actions can be 
  verified by asking questions or posting an image attachment that verifies the user did 
  the activity."""
  
  CONFIRM_CHOICES = (
    ('text', 'Text'),
    ('image', 'Image Upload'),
    ('code', 'Confirmation Code')
  )
  
  duration = models.IntegerField(
              verbose_name="Expected activity duration",
              help_text="Time (in minutes) that the activity is expected to take."
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
  users = models.ManyToManyField(User, through="ActivityMember")
  confirm_type = models.CharField(
                  max_length=20, 
                  choices=CONFIRM_CHOICES, 
                  default="text",
                  verbose_name="Confirmation Type"
                 )
  confirm_prompt = models.TextField(
                    blank=True, 
                    verbose_name="Confirmation prompt",
                    help_text="Text to display to user when requesting points (for images and codes)."
                   )
  is_event = models.BooleanField(default=False, verbose_name="Is Event?")
  event_date = models.DateTimeField(
                null=True, 
                blank=True, 
                verbose_name="Date and time of the event",
                help_text="Required for events."
               )
    
  def _is_active(self):
    """Determines if the activity is available for users to participate."""
    
    pub_result = datetime.date.today() - self.pub_date
    expire_result = self.expire_date - datetime.date.today()
    if pub_result.days < 0 or expire_result.days < 0:
      return False
    return True
    
  is_active = property(_is_active)
  
  def pick_question(self):
    """Choose a random question to present to a user."""
    if self.confirm_type != "text":
      return None
      
    questions = TextPromptQuestion.objects.filter(activity=self)
    return questions[random.randint(0, len(questions) - 1)]
    
  
  @staticmethod
  def get_available_for_user(user):
    """Retrieves only the activities that a user can participate in."""
    
    activities = Activity.objects.exclude(
      activitymember__user__username=user.username,
    )
    return (item for item in activities if item.is_active) # Filters out inactive activities.

def activity_image_file_path(instance=None, filename=None, user=None):
  """Returns the file path used to save an activity confirmation image."""

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
  
  def __unicode__(self):
    return "%s : %s" % (self.activity.title, self.user.username)
  
  def save(self):
    """Custom save method to award points to users if the item is approved."""
    
    if self.approval_status == u"approved" and not self.awarded:
      profile = self.user.get_profile()
      profile.points += self.activity.point_value
      profile.save()
      self.awarded = True
      
    elif self.approval_status != u"approved" and self.awarded:
      # Do we want to re-enable the confirmation code?
      profile = self.user.get_profile()
      profile.points -= self.activity.point_value
      profile.save()
      self.awarded = False
      
    super(ActivityMember, self).save()
    
  def delete(self):
    """Custom delete method to remove awarded points."""
    
    if self.awarded:
      # Do we want to re-enable the confirmation code?
      profile = self.user.get_profile()
      profile.points -= self.activity.point_value
      profile.save()
    
    super(ActivityMember, self).delete()

class Goal(CommonActivity):
  """Represents activities that are committed to by a group (floor)."""
  
  groups = models.ManyToManyField(Tribe, through="GoalMember")
  
class GoalMember(CommonActivityUser):
  """Represents the join between groups/floors."""
  
  group = models.ForeignKey(Tribe)
  goal = models.ForeignKey(Goal)
  
