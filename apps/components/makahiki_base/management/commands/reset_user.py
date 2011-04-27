import datetime
import random

from django.core import management
from django.conf import settings
from django.contrib.auth.models import User

class Command(management.base.BaseCommand):
  help = 'Resets the user(s) as if they never took part in the competition.'
  
  def handle(self, *args, **options):
    """
    Resets the user as if they never took part in the competition.
    """
    self.stdout.write("\nWARNING: This command will reset %s.  This process is irreversible.\n", args.join(" "))
    value = raw_input("Do you wish to continue (Y/n)? ")
    while value != "Y" and value != "n":
      self.stdout.write("Invalid option %s\n" % value)
      value = raw_input("Do you wish to continue (Y/n)? ")
    if value == "n":
      self.stdout.write("Operation cancelled.\n")
      return
      
    if len(args) == 0:
      self.stdout.write("Need at least one username to reset.\n")
      return
      
    users = []
    for arg in args:
      try:
        users.append(User.objects.get(username=arg))
      except User.DoesNotExist:
        self.stdout.write("User '%s' does not exist. Aborting.\n" % (arg,))
        return
        
    for user in users:
      self.stdout.write("Resetting user %s\n" % user.username)
      self.delete_members(user)
      self.reset_user(user)
      

  def delete_members(self, user):
    """
    Deletes the user's activities, commitments, quests, badges, and tickets.
    """
    for member in user.activitymember_set.all():
      member.delete()
    for member in user.commitmentmember_set.all():
      member.delete()
    for member in user.questmember_set.all():
      member.delete()
    for ticket in user.raffleticket_set.all():
      ticket.delete()
    for awarded in user.badges_earned.all():
      awarded.delete()
    for vote in user.energygoalvote_set.all():
      vote.delete()
      
  def reset_user(self, user):
    """
    Resets user attributes, like their score or if they did the first login.
    """
    profile = user.get_profile()
    profile.points = 0
    profile.last_awarded_submission = None
    profile.setup_profile = False
    profile.setup_complete = False
    profile.save()
    
    if user.facebookprofile:
      user.facebookprofile.delete()
      
    for entry in profile.scoreboardentry_set.all():
      entry.points = 0
      entry.last_awarded_submission = None
      entry.save()