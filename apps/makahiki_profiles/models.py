import os
import datetime

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist

from floors.models import Floor

from django.conf import settings

class InvalidRoundException(Exception):
  def __init__(self, value):
    self.value = value
    
  def __str__(self):
    return repr(self.value)
  
def _get_rounds():
  """Retrieves the rounds from the competition settings in a format that can be used in the ScoreboardEntry model."""
  
  return ((key, key) for key in settings.COMPETITION_ROUNDS.keys())

class ScoreboardEntry(models.Model):
  """Defines a class that tracks the user's scores in the rounds of the competition."""
  
  profile = models.ForeignKey("Profile", editable=False)
  round_name = models.CharField(max_length="30", choices=_get_rounds(), editable=False)
  points = models.IntegerField(default=0, editable=False)
  last_awarded_submission = models.DateTimeField(null=True, blank=True, editable=False)

def _get_available_themes():
  """Retrieves the available themes from the media folder."""
  
  theme_dir = os.path.join(settings.PROJECT_ROOT, "media")
  # Returns a list of tuples representing the name of the theme and the directory of the theme
  return ((item, item) for item in os.listdir(theme_dir) 
                      if os.path.isdir(os.path.join(theme_dir, item, "css")))
  
class Profile(models.Model):
    user = models.ForeignKey(User, unique=True, verbose_name=_('user'))
    name = models.CharField(_('name'), max_length=50)
    first_name = models.CharField(_('first_name'), max_length=50, null=True, blank=True)
    last_name = models.CharField(_('last_name'), max_length=50, null=True, blank=True)
    about = models.TextField(_('about'), null=True, blank=True)
    points = models.IntegerField(default=0, editable=False)
    last_awarded_submission = models.DateTimeField(null=True, blank=True, editable=False)
    theme = models.CharField(max_length=255, default="default", choices=_get_available_themes())
    floor = models.ForeignKey(Floor, null=True, blank=True)
    
    def __unicode__(self):
        return self.user.username
    
    def get_absolute_url(self):
        return ('profile_detail', None, {'username': self.user.username})
    get_absolute_url = models.permalink(get_absolute_url)
    
    def add_points(self, points, submission_date):
      """
      Adds points based on the point value of the submitted object.
      Note that this method does not save the profile.
      """
      self.points += points
      if not self.last_awarded_submission or submission_date > self.last_awarded_submission:
        self.last_awarded_submission = submission_date
        
      current_round = self._get_round(submission_date)
          
      # If we have a round, then update the scoreboard entry.  Otherwise, this just counts towards overall.
      if current_round:
        entry, created = ScoreboardEntry.objects.get_or_create(profile=self, round_name=current_round)
        entry.points += points
        if not entry.last_awarded_submission or submission_date > entry.last_awarded_submission:
          entry.last_awarded_submission = submission_date
        entry.save()
      
    def remove_points(self, points, submission_date):
      """Removes points from the user. Note that this method does not save the profile.  
      If the submission date is the same as the last_awarded_submission field, we rollback to a previously completed task."""
      self.points -= points
      
      current_round = self._get_round(submission_date)
          
      # If we have a round, then update the scoreboard entry.  Otherwise, this just counts towards overall.
      if current_round:
        try:
          entry = ScoreboardEntry.objects.get(profile=self, round_name=current_round)
          entry.points -= points
          if entry.last_awarded_submission == submission_date:
            # Need to find the previous update.
            entry.last_awarded_submission = self._last_submitted_before(submission_date)
            
          entry.save()
        except ObjectDoesNotExist:
          # This should not happen once the competition is rolling.
          raise InvalidRoundException("Attempting to remove points from a round when the user has no points in that round.")
        
      if self.last_awarded_submission == submission_date:
        self.last_awarded_submission = self._last_submitted_before(submission_date)
        
    def _get_round(self, submission_date):
      """Get the round that the submission date corresponds to.  Returns None if it doesn't correspond to anything."""
      
      rounds = settings.COMPETITION_ROUNDS
      
      # Find which round this belongs to.
      for key in rounds:
        start = datetime.datetime.strptime(rounds[key]["start"], "%Y-%m-%d")
        end = datetime.datetime.strptime(rounds[key]["end"], "%Y-%m-%d")
        if submission_date >= start and submission_date < end:
          return key
      
      return None
        
    def _last_submitted_before(self, submission_date):
      """Time of the last task that was completed before the submission date.  Returns None if there are no other tasks."""
      
      from activities.models import CommitmentMember, ActivityMember
      
      last_date = None
      try:
        # In the case of commitments, the award date is the same as the submission date.
        last_commitment = CommitmentMember.objects.filter(
            user=self.user,
            award_date__isnull=False,
            award_date__lt=submission_date
        ).latest("award_date").award_date
        last_date = last_commitment
      except CommitmentMember.DoesNotExist:
        pass
        
      try:
        last_activity = ActivityMember.objects.filter(
            user=self.user,
            approval_status=u"approved",
            submission_date__lt=submission_date
        ).latest("submission_date").submission_date
        if not last_date or last_date < last_activity:
          last_date = last_activity
      except ActivityMember.DoesNotExist:
        pass
      
      return last_date
      
    class Meta:
      verbose_name = _('profile')
      verbose_name_plural = _('profiles')

def create_profile(sender, instance=None, **kwargs):
    if instance is None:
        return
    profile, created = Profile.objects.get_or_create(user=instance)
    for key in settings.COMPETITION_ROUNDS.keys():
      entry, created = ScoreboardEntry.objects.get_or_create(profile=profile, round_name=key)

post_save.connect(create_profile, sender=User)

  
  
