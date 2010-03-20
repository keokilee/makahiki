import datetime

from django.db import models
from django.contrib.auth.models import User
from tribes.models import Tribe

from activities import ACTIVITY_FILE_DIR

# Create your models here.

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
  users = models.ManyToManyField(User, through="CommitmentMember")
    
class CommitmentMember(CommonBase):
  user = models.ForeignKey(User)
  commitment = models.ForeignKey(Commitment)
  is_active = models.BooleanField(default=True)
  comment = models.TextField()
      
class Activity(CommonActivity):
  confirm_code = models.CharField(blank=True, max_length=20)
  pub_date = models.DateField(default=datetime.date.today())
  expire_date = models.DateField()
  users = models.ManyToManyField(User, through="ActivityMember")
  
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

class EventActivity(Activity):
  event_date = models.DateTimeField()

def activity_image_file_path(instance=None, filename=None):
    user = instance.user
    return os.path.join(ACTIVITY_FILE_DIR, user.username, filename)
      
class ActivityMember(CommonBase):
  user = models.ForeignKey(User)
  activity = models.ForeignKey(Activity)
  comment = models.TextField()
  confirm_image = models.ImageField(null=True, upload_to=activity_image_file_path)
  is_confirmed = models.BooleanField(default=False)

class Goal(CommonActivity):
  groups = models.ManyToManyField(Tribe, through="GoalMember")
  
class GoalMember(CommonBase):
  group = models.ForeignKey(Tribe)
  goal = models.ForeignKey(Goal)
  is_confirmed = models.BooleanField()
