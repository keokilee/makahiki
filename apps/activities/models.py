import datetime
import random
import string
import os

from django.db import models, IntegrityError
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic

from makahiki_profiles.models import Profile
from floors.models import Floor, Post
from makahiki_base.models import Like

  
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
  
  MARKDOWN_LINK = "http://daringfireball.net/projects/markdown/syntax"
  MARKDOWN_TEXT = "Uses <a href=\"" + MARKDOWN_LINK + "\" target=\"_blank\">Markdown</a> formatting."
  
  title = models.CharField(max_length=200)
  description = models.TextField(help_text=MARKDOWN_TEXT)
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
  
  @staticmethod
  def get_available_for_user(user):
    """Filter out commitments the user is currently active in."""
    commitments = Commitment.objects.exclude(
      commitmentmember__user__username=user.username,
      commitmentmember__completed=False,
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
    profile = self.user.get_profile()
    
    if not self.completion_date:
      self.completion_date = datetime.date.today() + datetime.timedelta(days=self.commitment.duration)
      
    if not self.pk and profile.floor:
      message = "is participating in the commitment \"%s\"." % (
        self.commitment.title,
      )
      post = Post(user=self.user, floor=profile.floor, text=message, style_class="system_post")
      post.save()
      
    if self.completed:
      message = "has completed the commitment \"%s\"." % (
        self.commitment.title,
      )
      post = Post(user=self.user, floor=self.user.get_profile().floor, text=message, style_class="system_post")
      post.save()

    super(CommitmentMember, self).save()
  
  def delete(self):
    """Custom delete method to remove the points for completed commitments."""
    profile = self.user.get_profile()
    
    if self.completed:
      profile.points -= self.commitment.point_value
      profile.save()
    elif profile.floor:
      message = "is no longer participating in \"%s\"." % (
        self.commitment.title,
      )
      post = Post(user=self.user, floor=self.user.get_profile().floor, text=message, style_class="system_post")
      post.save()
      
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
          # print code.code
          # Throws exception if the code is a duplicate.
          code.save()
          valid = True
        except IntegrityError as error:
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
  likes  = generic.GenericRelation(Like)
  
  def _is_active(self):
    """Determines if the activity is available for users to participate."""
    
    pub_result = datetime.date.today() - self.pub_date
    expire_result = self.expire_date - datetime.date.today()
    if pub_result.days < 0 or expire_result.days < 0:
      return False
    return True
    
  is_active = property(_is_active)
  
  def liked_users(self):
    """Returns an array of users that like this activity."""
    return [like.user for like in self.likes.all()]
  
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
  
  from activities import ACTIVITY_FILE_DIR
  
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
      
      if profile.floor:
        message = " has been awarded %d points for completing \"%s\"." % (
          self.activity.point_value,
          self.activity.title,
        )
        post = Post(user=self.user, floor=profile.floor, text=message, style_class="system_post")
        post.save()
      
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
  
  floors = models.ManyToManyField(Floor, through="GoalMember")
  likes  = generic.GenericRelation(Like)
  
  @staticmethod
  def get_available_for_user(user):
    """Retrieves only the goals that a user can participate in."""
    
    return Goal.objects.exclude(
      goalmember__floor__pk=user.get_profile().floor.pk,
    )
    
class GoalMember(CommonActivityUser):
  """Represents the join between groups/floors."""
  
  goal = models.ForeignKey(Goal)
  floor = models.ForeignKey(Floor)
  user = models.ForeignKey(User)
  user_comment = models.TextField(null=True, blank=True, help_text="Comment from user about their submission.")
  admin_comment = models.TextField(null=True, blank=True, help_text="Reason for approval/rejection")
  
  def __unicode__(self):
    return "%s : %s Floor %d" % (self.goal.title, self.floor.dorm.name, self.floor.floor_number)
    
  @staticmethod
  def can_add_goal(user):
    """Method that determines if the user can add additional goals for their floor or not.
       A user cannot add a goal if they have more than two active goals or if their floor is 
       participating in more than five. """
    user_goals = user.goalmember_set.filter(
      awarded=False,
    )
    floor_goals = user.get_profile().floor.goalmember_set.filter(
      awarded=False,
    )
    
    if len(user_goals) < 2 and len(floor_goals) < 5:
      return True
      
    return False
    
  def can_manage_goal(user):
    """Simple method to determine if the goal belongs to the user."""
    return self.user == user
  
  def save(self):
    """Custom save method to award points to all floor members."""
    profile = self.user.get_profile()
    
    if not self.pk:
      message = " has added the goal \"%s\" to the floor." % (
        self.goal.title,
      )
      post = Post(user=self.user, floor=profile.floor, text=message, style_class="system_post")
      post.save()

    
    elif self.approval_status == u"approved" and not self.awarded:
      for profile in self.floor.profile_set.all():
        profile.points += self.goal.point_value
        profile.save()
        
        message = "'s goal \"%s\" has been completed! Everyone on the floor received %d points." % (
          self.goal.title,
          self.goal.point_value,
        )
        post = Post(user=self.user, floor=profile.floor, text=message, style_class="system_post")
        post.save()
      
      self.awarded = True
    
    elif self.approval_status !=u"approved" and self.awarded:
      for profile in self.floor.profile_set.all():
        profile.points -= self.goal.point_value
        profile.save()
        
      self.awarded = False
      
    super(GoalMember, self).save()
  
  def delete(self):
    """Custom delete method to remove points from all floor members."""
    
    if self.awarded:
      for profile in self.floor.profile_set.all():
        profile.points -= self.goal.point_value
        profile.save()
    
    super(GoalMember, self).delete()