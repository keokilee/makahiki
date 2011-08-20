import datetime

from django.db import models
from django.contrib.auth.models import User

from components.floors.models import Floor

# Create your models here.

class EnergyGoal(models.Model):
  start_date = models.DateField(help_text="The date on which the goal starts.  Users will begin voting at 12:00am on this date.")
  voting_end_date = models.DateField(help_text="The date on which voting ends. Voting ends at 12:00am on this date and the goal starts.")
  end_date = models.DateField(help_text="The goal will end at 12:00am on this date.")
  minimum_goal = models.IntegerField(default=0, help_text="The lowest percent reduction possible for a goal.")
  maximum_goal = models.IntegerField(default=50, help_text="The highest percent reduction possible for a goal.")
  goal_increments = models.IntegerField(default=5, help_text="The percent increments users will be able to vote on.")
  default_goal = models.IntegerField(
      default=5, 
      help_text="The default percent reduction that will appear in the voting form." + 
                "This must be a multiple of the goal increments between the minimum and maximum goal."
  )
  point_conversion = models.FloatField(
      default=1.0,
      help_text="The points awarded for this goal will be the percent reduction multiplied by this number.",
  )
  created_at = models.DateTimeField(editable=False, auto_now_add=True)
  updated_at = models.DateTimeField(editable=False, auto_now=True)
  
  def __unicode__(self):
    return "Goal for %s to %s" % (self.start_date, self.end_date)
    
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
    
  def get_floor_results(self, floor):
    """Get the floor's voting results for this goal."""
    votes = self.energygoalvote_set.filter(
      user__profile__floor=floor,
    ).values("percent_reduction").annotate(votes=models.Count('id')).order_by("-votes", "-percent_reduction")
        
    return votes
    
class EnergyGoalVote(models.Model):
  user = models.ForeignKey(User, editable=False)
  goal = models.ForeignKey(EnergyGoal, editable=False)
  percent_reduction = models.IntegerField(default=5)
  created_at = models.DateTimeField(editable=False, auto_now_add=True)
  
  class Meta:
    # Ensures that a user can only vote on a single goal.
    unique_together = ("user", "goal")
    
class FloorEnergyGoal(models.Model):
  # The amount of points to award for completing a goal.
  GOAL_POINTS = 20
  
  floor = models.ForeignKey(Floor)
  # goal = models.ForeignKey(EnergyGoal)
  percent_reduction = models.IntegerField(default=0, editable=False)
  goal_usage = models.DecimalField(decimal_places=2, max_digits=10, editable=False)
  actual_usage = models.DecimalField(decimal_places=2, max_digits=10, editable=False)
  
  created_at = models.DateTimeField(editable=False, auto_now_add=True)
  updated_at = models.DateTimeField(editable=False, auto_now=True)
  
  def save(self, *args, **kwargs):
    """Overrided save method to award the goal's points to members of the floor."""
    goal_completed = self.goal_usage and self.actual_usage and (self.actual_usage <= self.goal_usage)
    if self.floor and goal_completed:
      # Award points to the members of the floor.
      for profile in self.floor.profile_set.all():
        if profile.setup_complete:
          today = datetime.datetime.today()
          # Hack to get around executing this script at midnight.  We want to award
          # points earlier to ensure they are within the round they were completed.
          if today.hour == 0:
            today = today - datetime.timedelta(hours=1)

          profile.add_points(self.GOAL_POINTS, today)
          profile.save()
          
      
    super(FloorEnergyGoal, self).save(*args, **kwargs)
