import datetime

from django.db import models
from django.contrib.auth.models import User
from tribes.models import Tribe

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
  comment = models.TextField(null=True)
  
class Activity(CommonActivity):
  confirm_code = models.CharField(max_length=20)
  time = models.DateTimeField(null=True)
  users = models.ManyToManyField(User, through="ActivityMember")
  
  def _is_active(self):
    """Determines if the activity is available for users to participate."""
    if self.time:
      result = self.time - datetime.datetime.today()  
      if result.days > 5 or result.days < -5:
        return False    
    return True
  is_active = property(_is_active)
  
  @staticmethod
  def get_active_for_user(user):
    """Retrieves only the activities that a user can participate in."""
    activities = Activity.objects.exclude(activitymember__user__username=user.username)
    return (item for item in activities if item.is_active) # Filters out inactive activities.

class ActivityMember(CommonBase):
  user = models.ForeignKey(User)
  activity = models.ForeignKey(Activity)
  comment = models.TextField(null=True)
  is_confirmed = models.BooleanField(default=False)

class Goal(CommonActivity):
  groups = models.ManyToManyField(Tribe, through="GoalMember")
  
class GoalMember(CommonBase):
  group = models.ForeignKey(Tribe)
  goal = models.ForeignKey(Goal)
  is_confirmed = models.BooleanField()
