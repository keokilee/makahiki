import datetime

from django.db import models
from django.contrib.auth.models import User
from tribes.models import Tribe

# Create your models here.

class CommonActivity(models.Model):
  title = models.CharField(max_length=200)
  description = models.TextField()
  point_value = models.IntegerField()
  created_at = models.DateTimeField(editable=False)
  
  def __unicode__(self):
    return self.title
    
  def save(self):
    if not self.id:
      self.created_at = datetime.date.today()
    super(CommonActivity, self).save()
    
  class Meta:
    abstract = True

class Commitment(CommonActivity):
  users = models.ManyToManyField(User, through="CommitmentMember")
    
class CommitmentMember(models.Model):
  user = models.ForeignKey(User)
  commitment = models.ForeignKey(Commitment)
  created_at = models.DateTimeField(editable=False)
  is_active = models.BooleanField()
  comment = models.TextField(null=True)
  
  def save(self):
    if not self.id:
      self.created_at = datetime.date.today()
    super(CommitmentMember, self).save()
  
class Activity(CommonActivity):
  confirm_code = models.CharField(max_length=20)
  time = models.DateTimeField(null=True)
  users = models.ManyToManyField(User, through="ActivityMember")
  
class ActivityMember(models.Model):
  user = models.ForeignKey(User)
  activity = models.ForeignKey(Activity)
  created_at = models.DateTimeField()
  comment = models.TextField(null=True)
  is_confirmed = models.BooleanField(default=False)
  
  def save(self):
    if not self.id:
      self.created_at = datetime.date.today()
    super(ActivityMember, self).save()

class Goal(CommonActivity):
  groups = models.ManyToManyField(Tribe, through="GoalMember")
  
class GoalMember(models.Model):
  group = models.ForeignKey(Tribe)
  goal = models.ForeignKey(Goal)
  created_at = models.DateTimeField()
  is_confirmed = models.BooleanField()
  
  def save(self):
    if not self.id:
      self.created_at = datetime.date.today()
    super(GoalMember, self).save()
