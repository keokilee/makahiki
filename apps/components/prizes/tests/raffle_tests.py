import os
import datetime

from django.test import TestCase
from django.conf import settings
from django.core.files.images import ImageFile
from django.contrib.auth.models import User

from components.prizes.models import RafflePrize, RaffleTicket
from components.floors.models import Dorm, Floor

class RafflePrizeTests(TestCase):
  """
  Tests the RafflePrize model.
  """
  def setUp(self):
    """
    Sets up a test individual prize for the rest of the tests.
    This prize is not saved, as the round field is not yet set.
    """
    image_path = os.path.join(settings.PROJECT_ROOT, "fixtures", "test_images", "test.jpg")
    image = ImageFile(open(image_path, "r"))
    self.prize = RafflePrize(
        title="Super prize!",
        description="A test prize",
        image=image,
    )
    
    self.saved_rounds = settings.COMPETITION_ROUNDS
    self.current_round = "Round 1"
    start = datetime.date.today()
    end = start + datetime.timedelta(days=7)
    
    settings.COMPETITION_ROUNDS = {
      "Round 1" : {
        "start": start.strftime("%Y-%m-%d"),
        "end": end.strftime("%Y-%m-%d"),
      },
    }
    
    # Create test dorms, floors, and users.
    self.dorms = [Dorm(name="Test Dorm %d" % i) for i in range(0, 2)]
    map(lambda d: d.save(), self.dorms)
    
    self.floors = [Floor(number=str(i), dorm=self.dorms[i % 2]) for i in range(0, 4)]
    map(lambda f: f.save(), self.floors)
    
    self.users = [User.objects.create_user("test%d" % i, "test@test.com") for i in range(0, 4)]
    
    # Assign users to floors.
    for index, user in enumerate(self.users):
      user.get_profile().floor = self.floors[index % 4]
      user.get_profile().save()