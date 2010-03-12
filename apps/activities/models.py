from django.db import models
from django.contrib.auth.models import User
from tribes.models import Tribe

# Create your models here.

class Commitment(models.Model):
  title = models.CharField(max_length=200)
  description = models.TextField()
  point_value = models.IntegerField()
  created_at = models.DateTimeField()
  users = models.ManyToManyField(User, through="CommitmentMembers")
  
class CommitmentMembers(models.Model):
  user = models.ForeignKey(User)
  commitment = models.ForeignKey(Commitment)
  created_at = models.DateTimeField()
  is_active = models.BooleanField()
  
class Activity(models.Model):
  title = models.CharField(max_length=200)
  description = models.TextField()
  point_value = models.IntegerField()
  created_at = models.DateTimeField()
  confirm_code = models.CharField(max_length=20)
  active_date = models.DateTimeField(null=True)
  users = models.ManyToManyField(User, through="ActivityMembers")
  
class ActivityMembers(models.Model):
  user = models.ForeignKey(User)
  activity = models.ForeignKey(Activity)
  created_at = models.DateTimeField()
  comment = models.TextField(null=True)
  is_confirmed = models.BooleanField(default=False)

class Goal(models.Model):
  title = models.CharField(max_length=200)
  description = models.TextField()
  point_value = models.IntegerField()
  created_at = models.DateTimeField()
  groups = models.ManyToManyField(Tribe, through="GoalMembers")
  
class GoalMembers(models.Model):
  group = models.ForeignKey(Tribe)
  goal = models.ForeignKey(Goal)
  created_at = models.DateTimeField()
  is_confirmed = models.BooleanField()
