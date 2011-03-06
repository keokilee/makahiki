from django.db import models
from django.conf import settings

from components.makahiki_base import get_round_info
from components.makahiki_profiles.models import Profile

class Prize(models.Model):
  """
  Represents a prize in the system.
  """
  ROUND_CHOICES = ((round_name, round_name) for round_name in get_round_info().keys())
  AWARD_TO_CHOICES = (
      ("individual_overall", "Individual (Overall)"),
      ("individual_floor",  "Individual (" + settings.COMPETITION_GROUP_NAME + ")"),
      ("individual_dorm", "Individual (Dorm)"),
      ("floor_overall", settings.COMPETITION_GROUP_NAME + " (Overall)"),
      ("floor_dorm", settings.COMPETITION_GROUP_NAME + " (Dorm)"),
      ("dorm", "Dorm"), # Not implemented yet.
  )
  AWARD_CRITERIA_CHOICES = (
      ("points", "Points"),
      ("energy", "Energy")
  )
  
  title = models.CharField(max_length=30)
  description = models.TextField()
  image = models.ImageField(max_length=1024, upload_to="prizes", blank=True)
  round_name = models.CharField(max_length=20, choices=ROUND_CHOICES)
  award_to = models.CharField(max_length=20, choices=AWARD_TO_CHOICES)
  award_criteria = models.CharField(max_length=20, choices=AWARD_CRITERIA_CHOICES)
  
  class Meta:
    unique_together = ("round_name", "award_to", "award_criteria")
  
  def num_awarded(self, floor=None):
    """
    Returns the number of prizes that will be awarded for this prize.
    """
    if self.award_to in ("individual_overall", "floor_overall", "dorm"):
      # For overall prizes, it is only possible to award one.
      return 1
    
  def leader(self, floor=None):
    if self.award_criteria == "points":
      return self._points_leader(floor)
    else:
      return self._energy_leader(floor)
      
  def _points_leader(self, floor):
    if self.award_to == "individual_overall":
      if self.round_name == "Overall":
        return Profile.overall_points_leaders(num_results=1)[0]
      else:
        return Profile.overall_points_leaders(num_results=1, round_name=self.round_name)[0]
    
    raise Exception("Not implemented yet.")
    
  def _energy_leader(self, floor):
    raise Exception("Not implemented yet.")


      