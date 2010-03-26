import datetime

from django.db import models
from django.contrib.auth.models import User
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
  
  approval_status = models.CharField(max_length=20, choices=STATUS_TYPES, editable=False)

class CommonActivity(CommonBase):
  """Common fields for activity models."""
  
  title = models.CharField(max_length=200)
  description = models.TextField()
  point_value = models.IntegerField()
  
  def __unicode__(self):
    return self.title
    
  class Meta:
    abstract = True

class Commitment(CommonActivity):
  """Commitments involve non-verifiable actions that a user can commit to.
  Typically, they will be worth fewer points than activities."""
  
  users = models.ManyToManyField(User, through="CommitmentMember")
    
class CommitmentMember(CommonBase):
  """Represents the join between commitments and users.  Has fields for 
  commenting on a commitment and whether or not the commitment is currently 
  active."""
  
  user = models.ForeignKey(User)
  commitment = models.ForeignKey(Commitment)
  is_active = models.BooleanField(default=True)
  comment = models.TextField()
  
class Activity(CommonActivity):
  """Activities involve verifiable actions that users commit to.  These actions can be 
  verified by asking questions or posting an image attachment that verifies the user did 
  the activity."""
  
  CONFIRM_CHOICES = (
    ('text', 'Text'),
    ('image', 'Image Upload'),
  )
  
  confirm_code = models.CharField(blank=True, max_length=20)
  pub_date = models.DateField(default=datetime.date.today())
  expire_date = models.DateField()
  users = models.ManyToManyField(User, through="ActivityMember")
  confirm_type = models.CharField(max_length=20, choices=CONFIRM_CHOICES)
  is_event = models.BooleanField(default=False)
  event_date = models.DateTimeField(null=True, blank=True)
    
  def _is_active(self):
    """Determines if the activity is available for users to participate."""
    
    pub_result = datetime.date.today() - self.pub_date
    expire_result = self.expire_date - datetime.date.today()
    if pub_result.days < 0 or expire_result.days < 0:
      return False
    return True
    
  is_active = property(_is_active)
  
  @staticmethod
  def get_available_for_user(user):
    """Retrieves only the activities that a user can participate in."""
    
    activities = Activity.objects.exclude(activitymember__user__username=user.username)
    return (item for item in activities if item.is_active) # Filters out inactive activities.

def activity_image_file_path(instance=None, filename=None):
  """Returns the file path used to save an activity confirmation image."""
  
  user = instance.user
  return os.path.join(ACTIVITY_FILE_DIR, user.username, filename)
      
class ActivityMember(CommonActivityUser):
  """Represents the join between users and activities."""
  
  user = models.ForeignKey(User)
  activity = models.ForeignKey(Activity)
  comment = models.TextField()
  confirm_image = models.ImageField(null=True, upload_to=activity_image_file_path)

class Goal(CommonActivity):
  """Represents activities that are committed to by a group (floor)."""
  
  groups = models.ManyToManyField(Tribe, through="GoalMember")
  
class GoalMember(CommonActivityUser):
  """Represents the join between groups/floors."""
  
  group = models.ForeignKey(Tribe)
  goal = models.ForeignKey(Goal)
