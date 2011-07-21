#!/usr/bin/env python
import sys

from os.path import abspath, dirname, join

from django.conf import settings
from django.core.management import setup_environ

try:
    import settings as settings_mod # Assumed to be in the same directory.
except ImportError:
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)
    
# setup the environment before we start accessing things in the settings.
setup_environ(settings_mod)

sys.path.insert(0, join(settings.PINAX_ROOT, "apps"))
sys.path.insert(0, join(settings.PROJECT_ROOT, "apps"))

    
from components.floors.models import Floor
        
def competition_summary():
  """
  Writes summary of competition to a file.  The following things are on each line:
  * Building
  * Lounge
  * Total points to date
  * User wall posts
  * Number of canopy members in the lounge.
  """
  if len(sys.argv) != 2:
    print "Usage: python competition_summary.py <filename to write to>"
    exit()
    
  with open(sys.argv[1], "w") as out:
    for floor in Floor.objects.all():
      posts = floor.post_set.filter(style_class="user_post").count()
      canopy_members = floor.profile_set.filter(canopy_member=True).count()
      out.write("%s,%s,%d,%d,%d\n" % (floor.dorm.name, floor.number, floor.points(), posts, canopy_members))
    

if __name__ == "__main__":
    competition_summary()
