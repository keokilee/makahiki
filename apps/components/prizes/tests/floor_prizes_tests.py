import os
import datetime

from django.test import TestCase
from django.conf import settings
from django.core.files.images import ImageFile
from django.contrib.auth.models import User

from components.prizes.models import Prize
from components.floors.models import Dorm, Floor

class DormFloorPrizeTests(TestCase):
  """
  Tests awarding a prize to a dorm floor points winner.
  """
  def setUp(self):
    """
    Sets up a test individual prize for the rest of the tests.
    This prize is not saved, as the round field is not yet set.
    """
    image_path = os.path.join(settings.PROJECT_ROOT, "fixtures", "test_images", "test.jpg")
    image = ImageFile(open(image_path, "r"))
    self.prize = Prize(
        title="Super prize!",
        description="A test prize",
        image=image,
        award_to="floor_dorm",
        competition_type="points",
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
    
  def testNumAwarded(self):
    """
    Checks that the number of prizes to award for this prize is the same as the number of dorms.
    """
    self.prize.round_name = "Round 1"
    self.prize.save()
    
    self.assertEqual(self.prize.num_awarded(self.floors[0]), len(self.dorms), 
        "One prize should be awarded to each of the dorms in the competition.")
    
  def testRoundLeader(self):
    """
    Tests that we can retrieve the overall individual points leader for a round prize.
    """
    self.prize.round_name = "Round 1"
    self.prize.save()
    
    # Test one user will go ahead in points.
    profile = self.users[0].get_profile()
    profile.add_points(10, datetime.datetime.today() - datetime.timedelta(minutes=1))
    profile.save()
    
    self.assertEqual(self.prize.leader(profile.floor), profile.floor, 
        "The user's floor is not leading in the prize.")
        
    # Test a user in a different dorm.
    profile1 = self.users[1].get_profile()
    profile1.add_points(profile.points + 1, datetime.datetime.today() - datetime.timedelta(minutes=1))
    profile1.save()
    
    self.assertEqual(self.prize.leader(profile.floor), profile.floor, 
        "The leader for this prize in first users dorm should not change.")
    self.assertEqual(self.prize.leader(profile1.floor), profile1.floor, 
        "The leader in profile1's dorm is not profile1.")
        
    # Test that a user in a different floor but same dorm changes the leader for the original user.
    profile2 = self.users[2].get_profile()
    profile2.add_points(profile.points + 1, datetime.datetime.today() - datetime.timedelta(minutes=1))
    profile2.save()
    
    self.assertEqual(self.prize.leader(profile.floor), profile2.floor, 
        "The leader for this prize did not change.")
    self.assertEqual(self.prize.leader(profile1.floor), profile1.floor, 
        "The leader in profile1's dorm is not profile1.")
    
  def testOverallLeader(self):
    """
    Tests that we can retrieve the overall individual points leader for a round prize.
    """
    self.prize.round = "Overall"
    self.prize.save()

    # Test one user will go ahead in points.
    profile = self.users[0].get_profile()
    profile.add_points(10, datetime.datetime.today() - datetime.timedelta(minutes=1))
    profile.save()
    
    self.assertEqual(self.prize.leader(profile.floor), profile.floor, 
        "The user's floor is not leading in the prize.")
        
    # Test a user in a different dorm.
    profile1 = self.users[1].get_profile()
    profile1.add_points(profile.points + 1, datetime.datetime.today() - datetime.timedelta(minutes=1))
    profile1.save()
    
    self.assertEqual(self.prize.leader(profile.floor), profile.floor, 
        "The leader for this prize in first users dorm should not change.")
    self.assertEqual(self.prize.leader(profile1.floor), profile1.floor, 
        "The leader in profile1's dorm is not profile1.")
        
    # Test that a user in a different floor but same dorm changes the leader for the original user.
    profile2 = self.users[2].get_profile()
    profile2.add_points(profile.points + 1, datetime.datetime.today() - datetime.timedelta(minutes=1))
    profile2.save()
    
    self.assertEqual(self.prize.leader(profile.floor), profile2.floor, 
        "The leader for this prize did not change.")
    self.assertEqual(self.prize.leader(profile1.floor), profile1.floor, 
        "The leader in profile1's dorm is not profile1.")
    
  def tearDown(self):
    """
    Deletes the created image file in prizes.
    """
    settings.COMPETITION_ROUNDS = self.saved_rounds
    self.prize.delete()
    
class OverallFloorPrizeTest(TestCase):
  """
  Tests awarding a prize to a dorm floor points winner.
  """
  def setUp(self):
    """
    Sets up a test individual prize for the rest of the tests.
    This prize is not saved, as the round field is not yet set.
    """
    image_path = os.path.join(settings.PROJECT_ROOT, "fixtures", "test_images", "test.jpg")
    image = ImageFile(open(image_path, "r"))
    self.prize = Prize(
        title="Super prize!",
        description="A test prize",
        image=image,
        award_to="floor_overall",
        competition_type="points",
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
    self.dorm = Dorm(name="Test Dorm")
    self.dorm.save()
    
    self.floors = [Floor(number=str(i), dorm=self.dorm) for i in range(0, 2)]
    map(lambda f: f.save(), self.floors)
    
    self.users = [User.objects.create_user("test%d" % i, "test@test.com") for i in range(0, 4)]
    
    # Assign users to floors.
    for index, user in enumerate(self.users):
      user.get_profile().floor = self.floors[index % 2]
      user.get_profile().save()
    
  def testNumAwarded(self):
    """
    Simple test to check that the number of prizes to be awarded is one.
    """
    self.prize.round_name = "Round 1"
    self.prize.save()

    self.assertEqual(self.prize.num_awarded(), 1, "This prize should not be awarded to more than one user.")
    
  def testRoundLeader(self):
    """
    Tests that we can retrieve the overall individual points leader for a round prize.
    """
    self.prize.round_name = "Round 1"
    self.prize.save()
    
    # Test one user will go ahead in points.
    profile = self.users[0].get_profile()
    profile.add_points(10, datetime.datetime.today() - datetime.timedelta(minutes=1))
    profile.save()
    
    self.assertEqual(self.prize.leader(profile.floor), profile.floor, 
        "The user's floor is not leading in the prize.")
        
    # Test that a user in a different floor changes the leader for the original user.
    profile2 = self.users[2].get_profile()
    profile2.add_points(profile.points + 1, datetime.datetime.today() - datetime.timedelta(minutes=1))
    profile2.save()
    
    self.assertEqual(self.prize.leader(profile.floor), profile2.floor, 
        "The leader for this prize did not change.")
    
  def testOverallLeader(self):
    """
    Tests that we can retrieve the overall individual points leader for a round prize.
    """
    self.prize.round = "Overall"
    self.prize.save()

    # Test one user will go ahead in points.
    profile = self.users[0].get_profile()
    profile.add_points(10, datetime.datetime.today() - datetime.timedelta(minutes=1))
    profile.save()
    
    self.assertEqual(self.prize.leader(profile.floor), profile.floor, 
        "The user's floor is not leading in the prize.")
        
    # Test that a user in a different floor but same dorm changes the leader for the original user.
    profile2 = self.users[2].get_profile()
    profile2.add_points(profile.points + 1, datetime.datetime.today() - datetime.timedelta(minutes=1))
    profile2.save()
    
    self.assertEqual(self.prize.leader(profile.floor), profile2.floor, 
        "The leader for this prize did not change.")
    
  def tearDown(self):
    """
    Deletes the created image file in prizes.
    """
    settings.COMPETITION_ROUNDS = self.saved_rounds
    self.prize.delete()