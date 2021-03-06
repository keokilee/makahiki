import os
import datetime

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.localflavor.us.models import PhoneNumberField

from components.floors.models import Floor
from components.makahiki_base import get_current_round
from components.prizes import POINTS_PER_TICKET
from components.cache.utils import invalidate_info_bar_cache

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
  
  class Meta:
    unique_together = (("profile", "round_name",),)
    ordering = ("round_name",)
    
  @staticmethod
  def user_round_overall_rank(user, round_name):
    entry, created = ScoreboardEntry.objects.get_or_create(
      profile=user.get_profile(), 
      round_name=round_name
    )
    
    # Check if the user has done anything.
    if entry.last_awarded_submission:
      return ScoreboardEntry.objects.filter(
          Q(points__gt=entry.points) | 
          Q(points=entry.points, last_awarded_submission__gt=entry.last_awarded_submission),
          round_name=round_name,
      ).count() + 1
      
    # Users who have not done anything yet are assumed to be last.
    return ScoreboardEntry.objects.filter(
        points__gt=entry.points,
        round_name=round_name,
    ).count() + 1
    
  @staticmethod
  def user_round_floor_rank(user, round_name):
    floor = user.get_profile().floor
    entry, created = ScoreboardEntry.objects.get_or_create(
      profile=user.get_profile(), 
      round_name=round_name
    )
    
    if entry.last_awarded_submission:
      return ScoreboardEntry.objects.filter(
          Q(points__gt=entry.points) | 
          Q(points=entry.points, last_awarded_submission__gt=entry.last_awarded_submission),
          profile__floor=floor,
          round_name=round_name,
      ).count() + 1
    else:
      return ScoreboardEntry.objects.filter(
          points__gt=entry.points,
          profile__floor=floor,
          round_name=round_name,
      ).count() + 1

def _get_available_themes():
  """Retrieves the available themes from the media folder."""
  
  theme_dir = os.path.join(settings.PROJECT_ROOT, "media", "css")
  # Returns a list of tuples representing the name of the theme and the directory of the theme
  return ((item, item) for item in os.listdir(theme_dir))
  
class Profile(models.Model):
  user = models.ForeignKey(User, unique=True, verbose_name=_('user'), related_name='profile')
  name = models.CharField(_('name'), unique=True, max_length=50)
  first_name = models.CharField(_('first_name'), max_length=50, null=True, blank=True)
  last_name = models.CharField(_('last_name'), max_length=50, null=True, blank=True)
  points = models.IntegerField(default=0, editable=False)
  last_awarded_submission = models.DateTimeField(null=True, blank=True, editable=False)
  floor = models.ForeignKey(Floor, null=True, blank=True)
  contact_email = models.EmailField(null=True, blank=True)
  contact_text = PhoneNumberField(null=True, blank=True)
  contact_carrier = models.CharField(max_length=50, null=True, blank=True)
  enable_help = models.BooleanField(default=True)
  canopy_member = models.BooleanField(default=False)
  canopy_karma = models.IntegerField(default=0, editable=False)
  
  # Check first login completion.
  setup_profile = models.BooleanField(default=False, editable=False)
  setup_complete = models.BooleanField(default=False, editable=False)
  completion_date = models.DateTimeField(null=True, blank=True, editable=False)
  
  # Check visits for daily visitor badge.
  daily_visit_count = models.IntegerField(default=0, editable=False)
  last_visit_date = models.DateField(null=True, blank=True)
  
  # Check for referrer
  referring_user = models.ForeignKey(User, null=True, blank=True, related_name='referred_profiles')
  referrer_awarded = models.BooleanField(default=False, editable=False)
  
  def __unicode__(self):
      return self.name
  
  def get_lounge_name(self):
    return self.floor.dorm.name + '-' + self.floor.number
    
  @staticmethod
  def points_leaders(num_results=10, round_name=None):
    """
    Returns the top points leaders out of all users.
    """
    if round_name:
      return Profile.objects.filter(
          scoreboardentry__round_name=round_name,
      ).order_by("-scoreboardentry__points", "-scoreboardentry__last_awarded_submission")[:num_results]
    
    return Profile.objects.all().order_by("-points", "-last_awarded_submission")[:num_results]
  
  def available_tickets(self):
    """
    Returns the number of raffle tickets the user has available.
    """
    total_tickets = self.points / POINTS_PER_TICKET
    allocated_tickets = self.user.raffleticket_set.count()
    
    return total_tickets - allocated_tickets
    
  def current_round_points(self):
    """Returns the amount of points the user has in the current round."""
    current_round = get_current_round()
    if current_round:
      return ScoreboardEntry.objects.get(profile=self, round_name=current_round).points
      
    return self.points
  
  def current_round_overall_rank(self):
    """Returns the overall rank of the user for the current round."""
    current_round = get_current_round()
    if current_round:
      return self.overall_rank(round_name=current_round)
      
    return None
    
  def current_round_floor_rank(self):
    """Returns the rank of the user for the current round in their own floor."""
    current_round = get_current_round()
    if current_round:
      return self.floor_rank(round_name=current_round)

    return None
  
  def floor_rank(self, round_name=None):
    """Returns the rank of the user in their own floor."""
    if round_name:
      return ScoreboardEntry.user_round_floor_rank(self.user, round_name)
    
    # Calculate the rank.  This counts the number of people who are on the floor that have more points 
    # OR have the same amount of points but a later submission date 
    if self.last_awarded_submission:
      return Profile.objects.filter(
          Q(points__gt=self.points) | 
          Q(points=self.points, last_awarded_submission__gt=self.last_awarded_submission),
          floor=self.floor,
          user__is_staff=False,
          user__is_superuser=False,
      ).count() + 1
    
    return Profile.objects.filter(
        points__gt=self.points,
        floor=self.floor,
        user__is_staff=False,
        user__is_superuser=False,
    ).count() + 1
      
    
  def overall_rank(self, round_name=None):
    if round_name:
      return ScoreboardEntry.user_round_overall_rank(self.user, round_name)
      
    # Compute the overall rank.  This counts the number of people that have more points 
    # OR have the same amount of points but a later submission date
    if self.last_awarded_submission:
      return Profile.objects.filter(
          Q(points__gt=self.points) |
          Q(points=self.points, last_awarded_submission__gt=self.last_awarded_submission),
          user__is_staff=False,
          user__is_superuser=False,
      ).count() + 1
    
    return Profile.objects.filter(
        points__gt=self.points,
        user__is_staff=False,
        user__is_superuser=False,
    ).count() + 1
  
  def canopy_karma_info(self):
    """
    Returns a dictionary containing the user's rank and the total number of canopy members.
    """
    query = Profile.objects.filter(canopy_member=True)
    return {
      "rank":query.filter(canopy_karma__gt=self.canopy_karma).count() + 1,
      "total": query.count(),
    }

  def _is_canopy_activity(self, related_object):
    return related_object != None and \
       ((hasattr(related_object, "activity") and related_object.activity.is_canopy)
        or
        (hasattr(related_object, "commitment") and related_object.commitment.is_canopy))

  def add_points(self, points, submission_date, message, related_object=None):
    """
    Adds points based on the point value of the submitted object.
    Note that this method does not save the profile.
    """
    # Create a transaction first.
    transaction = PointsTransaction(
        user=self.user,
        points=points,
        submission_date=submission_date,
        message=message,
    ) 
    if related_object:
      transaction.related_object = related_object
      
    transaction.save()
    
    # Invalidate info bar cache.
    invalidate_info_bar_cache(self.user)

    # canopy activity deal with karma
    if self._is_canopy_activity(related_object):
        self.canopy_karma += points
    else:
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

  def remove_points(self, points, submission_date, message, related_object=None):
    """
    Removes points from the user. Note that this method does not save the profile.  
    If the submission date is the same as the last_awarded_submission field, we rollback 
    to a previously completed task.
    """
    # Log the transaction.
    transaction = PointsTransaction(
        user=self.user,
        points=points * -1,
        submission_date=submission_date,
        message=message,
    )
    if related_object:
      transaction.related_object = related_object
    
    transaction.save()
    
    # Invalidate info bar cache.
    invalidate_info_bar_cache(self.user)

    if self._is_canopy_activity(related_object):
        self.canopy_karma -= points
    else:
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
    """
    Time of the last task that was completed before the submission date.  Returns None if there are no other tasks.
    """
    
    from components.activities.models import CommitmentMember, ActivityMember
    
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
    
  def save(self, *args, **kwargs):
    """
    Custom save method to check for referral bonus.
    """
    has_referral = self.referring_user is not None and not self.referrer_awarded
    referrer = None
    if has_referral and self.points >= 30:
      self.referrer_awarded = True
      referrer = Profile.objects.get(user=self.referring_user)
      self.add_points(10, datetime.datetime.today(), 'Referred by %s' % referrer.name, self)
      
    super(Profile, self).save(*args, **kwargs)
    
    if referrer:
      referrer.add_points(10, datetime.datetime.today(), 'Referred %s' % self.name, referrer)
      referrer.save()
      
  class Meta:
    verbose_name = _('profile')
    verbose_name_plural = _('profiles')

def create_profile(sender, instance=None, **kwargs):
  if (kwargs.get('created', True) and not kwargs.get('raw', False)):
    profile, created = Profile.objects.get_or_create(user=instance, name=instance.username)
    for key in settings.COMPETITION_ROUNDS.keys():
      entry, created = ScoreboardEntry.objects.get_or_create(profile=profile, round_name=key)

post_save.connect(create_profile, sender=User)

class PointsTransaction(models.Model):
  """
  Entries that track points awarded to users.
  """
  user = models.ForeignKey(User)
  points = models.IntegerField()
  submission_date = models.DateTimeField()
  message = models.CharField(max_length=255)
  object_id = models.PositiveIntegerField(null=True)
  content_type = models.ForeignKey(ContentType, null=True)
  related_object = generic.GenericForeignKey("content_type", "object_id") 
  
  @staticmethod
  def get_transaction_for_object(related_object, points):
    try:
      content_type = ContentType.objects.get_for_model(related_object)
      return PointsTransaction.objects.filter(
          points=points,
          object_id=related_object.id,
          content_type=content_type,
      )[0]
      
    except IndexError:
      return None
