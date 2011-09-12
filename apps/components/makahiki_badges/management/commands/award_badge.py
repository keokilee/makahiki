from django.core import management
from django.contrib.auth.models import User

from lib.brabeion import badges
from components.makahiki_badges import user_badges

def award_badge(slug, username):
  try:
    user = User.objects.get(username=username)
    badge = badges.possibly_award_badge(slug, user=user)
  except User.DoesNotExist:
    self.stderr.write("User with the username %s does not exist.\n" % username)
  except KeyError:
    self.stderr.write("Badge with the slug %s does not exist.\n" % slug)

class Command(management.base.BaseCommand):
  help = 'Awards a badge (identified by its slug) to a user.'
  
  def handle(self, *args, **options):
    """
   Awards a badge (identified by its slug) to a user
    """
    if len(args) != 2:
      self.stderr.write("Usage: 'python manage.py award_badge <badge-slug> <user>\n")
      return
      
    slug = args[0]
    username = args[1]
    
    award_badge(slug, username)