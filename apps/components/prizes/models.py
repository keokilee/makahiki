from django.db import models
from django.conf import settings

from components.makahiki_base import get_round_info
from components.makahiki_profiles.models import Profile

class BasePrize(models.Model):
  """
  Represents a prize in the system.
  """
  ROUND_CHOICES = ((round_name, round_name) for round_name in get_round_info().keys())
  # AWARD_TO_CHOICES = (
  #     ("individual_overall", "Overall Individual"),
  #     ("individual_floor", settings.COMPETITION_GROUP_NAME + " Individual"),
  #     ("floor", settings.COMPETITION_GROUP_NAME),
  #     # ("Dorm", "Dorm"), # Not implemented yet.
  # )
  # AWARD_CRITERIA_CHOICES = (
  #     ("points", "Points"),
  #     ("energy", "Energy")
  # )
  
  title = models.CharField(max_length=30)
  description = models.TextField()
  image = models.ImageField(max_length=1024, upload_to="prizes", blank=True)
  round_name = models.CharField(max_length=20, choices=ROUND_CHOICES, unique=True)
  
  class Meta:
    abstract = True

class IndividualOverallPointsPrize(BasePrize):
  @staticmethod
  def num_awarded(self):
    """
    Returns the possible number awarded, which in the case of the overall points winner is simply 1.
    """
    return 1
    
  def leader(self):
    """
    Returns the individual points leader.
    """
    if self.round_name == "Overall":
      return Profile.overall_points_leaders(num_results=1)[0]
    else:
      return Profile.overall_points_leaders(num_results=1, round_name=self.round_name)[0]

      