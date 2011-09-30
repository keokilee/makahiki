from django.core import management
from django.contrib.auth.models import User
from apps.components.floors.models import Floor

class Command(management.base.BaseCommand):
  help = 'load and create the users from a csv file containing lounge, name, and email'

  def handle(self, *args, **options):
    """
    Resets the user as if they never took part in the competition.
    """
    if len(args) == 0:
      self.stdout.write("the csv file name missing.\n")
      return

    filename = args[0]
    try:
        file = open(filename)
    except:
        self.stdout.write("Can not open the file: %s , Aborting.\n" % (filename))
        return

    for line in file:
        items = line.split(":")
        lounge_items = items[0].split()

        lounge = self.get_lounge(lounge_items[2], lounge_items[3])

        firstname = items[1].strip().capitalize()
        middlename = items[2].strip().capitalize()
        if middlename:
            firstname += " " + middlename
        
        lastname = items[3].strip().capitalize()
        email = items[4].strip()
        username = email.split("@")[0]
        print "%s,%s,%s,%s,%s" % (lounge, firstname, lastname, email, username)

        try:
          user = User.objects.get(username=username)
          user.delete()
        except:
          None
            
        user = User.objects.create_user(username, email)
        user.first_name = firstname
        user.last_name = lastname
        user.save()
        
        profile = user.get_profile()
        profile.first_name = firstname
        profile.last_name = lastname
        profile.floor = Floor.objects.get(floor_identifier=lounge)
        profile.save()

    file.close()

  def get_lounge(self, dorm, floor):
    if dorm == 'LE':
        dorm = 'Lehua'
    elif dorm == 'MO':
        dorm = 'Mokihana'
    elif dorm == 'IL':
        dorm = 'Ilima'
    elif dorm == 'LO':
        dorm = 'Lokelani'

    if floor == '03' or floor == '04':
        floor = 'A'
    elif floor == '05' or floor == '06':
        floor = 'B'
    elif floor == '07' or floor == '08':
        floor = 'C'
    elif floor == '09' or floor == '10':
        floor = 'D'
    elif floor == '11' or floor == '12':
        floor = 'E'

    return dorm + '-' + floor
