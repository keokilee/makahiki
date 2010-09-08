from django.db import models
from django.contrib.auth.models import User

from floors.models import Floor

# Create your models here.

class EnergyGoal(models.Model):
  start_date = models.DateField(help_text="The date on which the goal starts.  Users will begin voting on this date.")
  voting_end_date = models.DateField(help_text="The date on which voting ends.")
  end_date = models.DateField(help_text="The date on which the goal ends.")
  minimum_goal = models.IntegerField(default=0, help_text="The lowest percent reduction possible for a goal.")
  maximum_goal = models.IntegerField(default=50, help_text="The highest percent reduction possible for a goal.")
  goal_increments = models.IntegerField(default=5, help_text="The percent increments users will be able to vote on.")
  created_at = models.DateTimeField(editable=False)
  updated_at = models.DateTimeField(null=True, editable=False)
  
  def save(self):
    if not self.id:
      self.created_at = datetime.datetime.today()
    else:
      self.updated_at = datetime.datetime.today()
    super(EnergyGoal, self).save()
  
class EnergyGoalVote(models.Model):
  user = models.ForeignKey(User)
  goal = models.ForeignKey(EnergyGoal)
  percent_reduction = models.IntegerField(default=0, editable=False)
  created_at = models.DateTimeField(editable=False)
  
  def save(self):
    if not self.id:
      self.created_at = datetime.datetime.today()
    super(EnergyGoal, self).save()
    
class FloorEnergyGoal(models.Model):
  floor = models.ForeignKey(Floor)
  goal = models.ForeignKey(EnergyGoal)
  percent_reduction = models.IntegerField(default=0, editable=False)