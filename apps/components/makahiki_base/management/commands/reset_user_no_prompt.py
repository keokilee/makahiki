import datetime
import random
import string

from django.core import management
from django.conf import settings
from django.contrib.auth.models import User

from components.makahiki_facebook.models import FacebookProfile

class Command(management.base.BaseCommand):
  help = 'Resets the user(s) as if they never took part in the competition.'
    
  def handle(self, *args, **options):
    """
    Resets the user as if they never took part in the competition.
    """
    if len(args) == 0:
      self.stdout.write("Need at least one username to reset.\n")
      return
      
    self.stdout.write("WARNING: This command will reset the following user(s):\n%s" % (
        string.join(args, "\n")
    ))
    self.stdout.write("\n\nThis process is irreversible.\n") 
    users = []
    for arg in args:
      try:
        users.append(User.objects.get(username=arg))
      except User.DoesNotExist:
        self.stdout.write("User '%s' does not exist. Aborting.\n" % (arg,))
        return
        
    for user in users:
      self.stdout.write("Resetting user %s\n" % user.username)
      self.reset_user(user)
      
  def reset_user(self, user):
    """
    Resets user by deleting them and then restoring them. Preserves the following attributes:
    * username
    * email
    * staff/superuser status
    * display_name
    * First and last name
    * Floor/lounge
    """
    username = user.username
    email = user.email
    is_staff = user.is_staff
    is_superuser = user.is_superuser
    
    profile = user.get_profile()
    d_name = profile.name
    f_name = profile.first_name
    l_name = profile.last_name
    floor = profile.floor
    
    # Delete the user and create a new one.
    user.delete()
    new_user = User.objects.create_user(username=username, email=email, password="")
    new_user.is_staff = is_staff
    new_user.is_superuser = is_superuser
    new_user.save()
    
    profile = new_user.get_profile()
    profile.name = d_name
    profile.first_name = f_name
    profile.last_name = l_name
    profile.floor = floor
    
    profile.save()
