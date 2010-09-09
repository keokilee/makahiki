import datetime

from django.db import models
from django.contrib.auth.models import User

from floors.models import Floor

# Create your models here.

class EnergyGoal(models.Model):
  start_date = models.DateField(help_text="The date on which the goal starts.  Users will begin voting at 12:00am on this date.")
  voting_end_date = models.DateField(help_text="The date on which voting ends. Voting ends at 12:00am on this date and the goal starts.")
  end_date = models.DateField(help_text="The goal will end at 12:00am on this date.")
  minimum_goal = models.IntegerField(default=0, help_text="The lowest percent reduction possible for a goal.")
  maximum_goal = models.IntegerField(default=50, help_text="The highest percent reduction possible for a goal.")
  goal_increments = models.IntegerField(default=5, help_text="The percent increments users will be able to vote on.")
  created_at = models.DateTimeField(editable=False)
  updated_at = models.DateTimeField(null=True, editable=False)
  
  def __unicode__(self):
    return "Goal for %s to %s" % (self.start_date, self.end_date)
  
  def save(self):
    if not self.id:
      self.created_at = datetime.datetime.today()
    else:
      self.updated_at = datetime.datetime.today()
    super(EnergyGoal, self).save()
    
  @staticmethod
  def get_current_goal():
    """Gets the current energy goal. Returns None if no goal is currently going on."""
    today = datetime.date.today()
    for goal in EnergyGoal.objects.all():
      if today >= goal.start_date and today < goal.end_date:
        return goal
        
    return None
    
  def in_voting_period(self):
    """Returns True if the goal is in the voting period and False otherwise."""
    today = datetime.date.today()
    if today >= self.start_date and today < self.voting_end_date:
      return True
    
    return False
    
  def user_can_vote(self, user):
    """Determines if the user can vote."""
    for vote in self.energygoalvote_set.all():
      if vote.user == user:
        return False
        
    return True
  
class EnergyGoalVote(models.Model):
  user = models.ForeignKey(User, editable=False)
  goal = models.ForeignKey(EnergyGoal, editable=False)
  percent_reduction = models.IntegerField(default=0)
  created_at = models.DateTimeField(editable=False)
  
  class Meta:
    # Ensures that a user can only vote on a single goal.
    unique_together = ("user", "goal")
  
  def save(self):
    if not self.id:
      self.created_at = datetime.datetime.today()
    super(EnergyGoalVote, self).save()
    
class FloorEnergyGoal(models.Model):
  floor = models.ForeignKey(Floor)
  goal = models.ForeignKey(EnergyGoal)
  percent_reduction = models.IntegerField(default=0, editable=False)