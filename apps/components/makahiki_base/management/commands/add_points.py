import datetime

from django.core import management
from django.contrib.auth.models import User

from components.floors.models import Floor
from components.makahiki_notifications.models import UserNotification

class Command(management.base.BaseCommand):
  help = """
  Awards points to a username or a building and lounge.\n
  Usage is either:\n
  'python manage.py add_points <username> <points> <short-message> <long-message>' or\n
  'python manage.py add_points <residence-hall> <floor-number> <points> <short-message> <long-message>'\n
  """
  
  def handle(self, *args, **options):
    """
    Awards points to a user or a building and lounge.
    Format of the command is either:
      python manage.py add_points <username> <points> <short-message> <long-message>
      python manage.py add_points <residence-hall> <floor-number> <points> <short-message> <long-message>
    """
    if len(args) < 4 or len(args) > 5:
      usage = """
      Usage is either:\n
      'python manage.py add_points <username> <points> <short-message> <long-message>' or\n
      'python manage.py add_points <residence-hall> <floor-number> <points> <short-message> <long-message>'\n
      """
      self.stderr.write(usage)
      return 1
      
    today = datetime.datetime.today()
    # If there are 4 args, try and get the user.
    if len(args) == 4:
      try:
        user = User.objects.get(username=args[0])
        profile = user.get_profile()
        profile.add_points(int(args[1]), datetime.datetime.today(), args[2])
        profile.save()
        
        UserNotification.create_success_notification(user, args[3])
      except User.DoesNotExist:
        self.stderr.write("User with username %s does not exist" % args[0])
        return 1
    
    else:
      try:
        floor = Floor.objects.get(dorm__name=args[0], number=args[1])
        for profile in floor.profile_set.all():
          profile = user.get_profile()
          profile.add_points(int(args[2]), datetime.datetime.today(), args[3])
          profile.save()
          
          UserNotification.create_success_notification(profile.user, args[4])
          
      except Floor.DoesNotExist:
        self.stderr.write("Floor with building name %s and floor %s does not exist" % (args[0], args[1]))
        return 1
    