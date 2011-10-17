import datetime
import random
import string

from django.core import management
from django.conf import settings

from components.makahiki_profiles.models import Profile, PointsTransaction
from components.floors.models import Post
from components.canopy.models import Post as CanopyPost
from components.activities.models import EmailReminder, TextReminder, ActivityMember, CommitmentMember
from components.quests.models import QuestMember
from components.prizes.models import RaffleTicket
from components.energy_goals.models import FloorEnergyGoal
from lib.brabeion.models import BadgeAward

class Command(management.base.BaseCommand):
  help = 'Restore the competition to a pristine state.'
  
  def handle(self, *args, **options):
    """
    Restores the competition to a pristine state.
    """
    self.stdout.write("WARNING: This command will reset the competition to a pristine state. " + \
        "Points, wall posts, energy goals, raffle tickets, and activity/commitment/quest memberships will be removed.")
    self.stdout.write("\n\nThis process is irreversible.\n")
    value = raw_input("Do you wish to continue (Y/n)? ")
    while value != "Y" and value != "n":
      self.stdout.write("Invalid option %s\n" % value)
      value = raw_input("Do you wish to continue (Y/n)? ")
    if value == "n":
      self.stdout.write("Operation cancelled.\n")
      return
      
    self._reset_points()
    self._delete_points_log()
    self._delete_reminders()
    self._delete_memberships()
    self._delete_raffle_tickets()
    self._delete_energy_goals()
    self._delete_badges()
    self._delete_posts()
    
  def _reset_points(self):
    self.stdout.write('Resetting points.\n')
    for profile in Profile.objects.all():
      profile.points = 0
      profile.last_awarded_submission = datetime.datetime.today()
      profile.save()
      
      for entry in profile.scoreboardentry_set.all():
        entry.points = 0
        entry.last_awarded_submission = datetime.datetime.today()
        entry.save()
        
  def _delete_points_log(self):
    self.stdout.write('Deleting points transactions.\n')
    PointsTransaction.objects.all().delete()
        
  def _delete_posts(self):
    self.stdout.write('Deleting floor posts.\n')
    Post.objects.all().delete()
    self.stdout.write('Deleting canopy posts.\n')
    CanopyPost.objects.all().delete()
    
  def _delete_reminders(self):
    self.stdout.write('Deleting email reminders.\n')
    EmailReminder.objects.all().delete()
    self.stdout.write('Deleting text reminders.\n')
    TextReminder.objects.all().delete()
    
  def _delete_memberships(self):
    self.stdout.write('Deleting quest memberships.\n')
    QuestMember.objects.all().delete()
    self.stdout.write('Deleting activity memberships.\n')
    ActivityMember.objects.all().delete()
    self.stdout.write('Deleting commitment memberships.\n')
    CommitmentMember.objects.all().delete()
    
  def _delete_raffle_tickets(self):
    self.stdout.write('Deleting raffle tickets.\n')
    RaffleTicket.objects.all().delete()
    
  def _delete_energy_goals(self):
    self.stdout.write('Deleting energy goals.\n')
    FloorEnergyGoal.objects.all().delete()
    
  def _delete_badges(self):
    self.stdout.write('Deleting badge awarded objects.\n')
    BadgeAward.objects.all().delete()