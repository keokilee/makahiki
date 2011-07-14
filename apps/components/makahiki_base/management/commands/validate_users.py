import datetime
import random
import string

from django.core import management
from django.conf import settings
from django.contrib.auth.models import User

from components.makahiki_facebook.models import FacebookProfile

class Command(management.base.BaseCommand):
  help = 'Cleans out users with duplicate ids.  Renames users with duplicate display names.'
  
  def handle(self, *args, **options):
    """
    Cleans out users with duplicate ids.  Renames users with duplicate display names.
    """
    letters = "abcdefghijklmnopqrstuvwxyz".upper()
    
    names = Profile.objects.values("name").distinct()
    for name in names:
      profiles = Profile.objects.filter(name=name['name'])
      if profiles.count() > 1:
        print "%d profiles have the name %s" % (profiles.count(), name['name'])
        index = 0
        for profile in profiles:
          profile.name = "%s %s." % (profile.name, letters[index])
          profile.save()
          counter += 1

    users = Profile.objects.values("user").distinct()
    for user in users:
      profiles = Profile.objects.filter(user=user["user"])
      if profiles.count() > 1:
        print "Found %d profiles for user %d" % (profiles.count(), user["user"])
        for profile in profiles[1:]:
          profile.delete()