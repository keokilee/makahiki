import datetime
import random
import string
import os

from django.db import models, IntegrityError
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.conf import settings

from makahiki_profiles.models import Profile
from floors.models import Floor, Post
from makahiki_base.models import Like

MARKDOWN_LINK = "http://daringfireball.net/projects/markdown/syntax"
MARKDOWN_TEXT = "Uses <a href=\"" + MARKDOWN_LINK + "\" target=\"_blank\">Markdown</a> formatting."
  
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
  award_date = models.DateTimeField(null=True, blank=True, editable=False)
  submission_date = models.DateTimeField(null=True, blank=True, editable=False)

class Commitment(CommonBase):
  """Commitments involve non-verifiable actions that a user can commit to.
  Typically, they will be worth fewer points than activities."""
  
  title = models.CharField(max_length=200)
  description = models.TextField(help_text=MARKDOWN_TEXT)
  point_value = models.IntegerField()
  users = models.ManyToManyField(User, through="CommitmentMember")
  duration = models.IntegerField(default=5, help_text="Duration of commitment, in days.")
  
  def __unicode__(self):
    return self.title
    
class CommitmentMember(CommonBase):
  """Represents the join between commitments and users.  Has fields for 
  commenting on a commitment and whether or not the commitment is currently 
  active."""
  
  user = models.ForeignKey(User)
  commitment = models.ForeignKey(Commitment)
  award_date = models.DateTimeField(blank=True, null=True, editable=False)
  completion_date = models.DateField()
  comment = models.TextField(blank=True)
  
  def __unicode__(self):
    return "%s : %s" % (self.commitment.title, self.user.username)
  
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
      profile.add_points(self)
      profile.save()
      
      if profile.floor:
        # Construct the points
        message = "has completed the commitment \"%s\"." % (
          self.commitment.title,
        )

        post = Post(user=self.user, floor=self.user.get_profile().floor, text=message, style_class="system_post")
        post.save()

    super(CommitmentMember, self).save()
  
  def delete(self):
    """Custom delete method to remove the points for completed commitments."""
    profile = self.user.get_profile()
    
    if self.award_date:
      profile.remove_points(self)
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
      
class Activity(CommonBase):
  """Activities involve verifiable actions that users commit to.  These actions can be 
  verified by asking questions or posting an image attachment that verifies the user did 
  the activity."""
  
  CONFIRM_CHOICES = (
    ('text', 'Text'),
    ('image', 'Image Upload'),
    ('code', 'Confirmation Code')
  )
  
  title = models.CharField(max_length=200)
  description = models.TextField(help_text=MARKDOWN_TEXT)
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
                      
  def __unicode__(self):
    return self.title
  
  def _is_active(self):
    """Determines if the activity is available for users to participate."""
    
    pub_result = datetime.date.today() - self.pub_date
    expire_result = self.expire_date - datetime.date.today()
    if pub_result.days < 0 or expire_result.days < 0:
      return False
    return True
    
  is_active = property(_is_active)
  
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
  
  def pick_question(self):
    """Choose a random question to present to a user."""
    if self.confirm_type != "text":
      return None
      
    questions = TextPromptQuestion.objects.filter(activity=self)
    return questions[random.randint(0, len(questions) - 1)]

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
  points_awarded = models.IntegerField(
      blank=True, 
      null=True, 
      help_text="Number of points to award for activities with variable point values."
  )
  
  def __unicode__(self):
    return "%s : %s" % (self.activity.title, self.user.username)
  
  def save(self):
    """Custom save method to award/remove points if the activitymember is approved or rejected."""
    if self.approval_status == u"pending":
      # Mark pending items as submitted.
      self.submission_date = datetime.datetime.today()
      
    elif self.approval_status == u"approved" and not self.award_date:
      # Award users points and update wall.
      self.award_date = datetime.datetime.today()
      if not self.submission_date:
        # This may happen if it is an item with a confirmation code.
        self.submission_date = self.award_date
      profile = self.user.get_profile()
      profile.add_points(self)
      profile.save()
      
      if profile.floor:
        # Post on the user's floor wall.
        if self.activity.has_variable_points:
          points = self.points_awarded
        else:
          points = self.activity.point_value
          
        message = " has been awarded %d points for completing \"%s\"." % (
          points,
          self.activity.title,
        )
        post = Post(user=self.user, floor=profile.floor, text=message, style_class="system_post")
        post.save()
      
    elif self.approval_status != u"approved" and self.award_date:
      # Removing user points and resetting award date.
      profile = self.user.get_profile()
      profile.remove_points(self)
      profile.save()
      self.award_date = None
      self.submission_date = None # User will have to resubmit.
      
      
    super(ActivityMember, self).save()
    
  def delete(self):
    """Custom delete method to remove awarded points."""
    
    if self.approval_status == u"approved":
      profile = self.user.get_profile()
      profile.remove_points(self)
      profile.save()
      
    super(ActivityMember, self).delete()

class Goal(CommonBase):
  """Represents activities that are committed to by a group (floor)."""
  
  title = models.CharField(max_length=200)
  description = models.TextField(help_text=MARKDOWN_TEXT)
  point_value = models.IntegerField()
  floors = models.ManyToManyField(Floor, through="GoalMember")
  likes  = generic.GenericRelation(Like)
  
  def __unicode__(self):
    return self.title
  
  def liked_users(self):
    """Returns an array of users that like this activity."""
    return [like.user for like in self.likes.all()]
    
class GoalMember(CommonActivityUser):
  """Represents the join between groups/floors."""
  
  goal = models.ForeignKey(Goal)
  floor = models.ForeignKey(Floor)
  user = models.ForeignKey(User)
  user_comment = models.TextField(null=True, blank=True, help_text="Comment from user about their submission.")
  admin_comment = models.TextField(null=True, blank=True, help_text="Reason for approval/rejection")
  
  def __unicode__(self):
    if settings.COMPETITION_GROUP_NAME:
      floor_label = settings.COMPETITION_GROUP_NAME
    else:
      floor_label = "Floor"
    return "%s : %s %s %s" % (self.goal.title, self.floor.dorm.name, floor_label, self.floor.number)
    
  @staticmethod
  def can_add_goal(user):
    """Method that determines if the user can add additional goals for their floor or not.
       A user cannot add a goal if they have MAX_USER_GOALS or if their floor is 
       participating in MAX_FLOOR_GOALS. """
      
    from activities import MAX_USER_GOALS, MAX_FLOOR_GOALS
    
    user_goals = user.goalmember_set.filter(
      award_date=None,
    ).count()
    floor_goals = user.get_profile().floor.goalmember_set.filter(
      award_date=None,
    ).count()
    
    if user_goals < MAX_USER_GOALS and floor_goals < MAX_FLOOR_GOALS:
      return True
      
    return False
    
  def can_manage_goal(user):
    """Simple method to determine if the goal belongs to the user."""
    return self.user == user
  
  def save(self):
    """Custom save method to award points to all floor members."""
    profile = self.user.get_profile()
    
    if not self.pk:
      # Item is being saved for the first time.
      message = " has added the goal \"%s\" to the floor." % (
        self.goal.title,
      )
      post = Post(user=self.user, floor=profile.floor, text=message, style_class="system_post")
      post.save()
    
    if self.approval_status == u"pending":
      # Mark pending items as submitted.
      self.submission_date = datetime.datetime.today()
    
    elif self.approval_status == u"approved" and not self.award_date:
      # Award points to users and post on the floor wall.
      self.award_date = datetime.datetime.today()
      if not self.submission_date:
        self.submission_date = self.award_date
      for profile in self.floor.profile_set.all():
        profile.add_points(self)
        profile.save()
      
      message = "'s goal \"%s\" has been completed! Everyone on the floor received %d points." % (
        self.goal.title,
        self.goal.point_value,
      )
      post = Post(user=self.user, floor=profile.floor, text=message, style_class="system_post")
      post.save()
    
    elif self.approval_status != u"approved" and self.award_date:
      # Remove points and reject goal.
      for profile in self.floor.profile_set.all():
        profile.remove_points(self)
        profile.save()
      self.award_date = None
      self.submission_date = None
      
    super(GoalMember, self).save()
      
        
  def delete(self):
    """Custom delete method to remove points from all floor members."""
    if self.award_date:
      for profile in self.floor.profile_set.all():
        profile.remove_points(self)
        profile.save()
        
    super(GoalMember, self).delete()
    