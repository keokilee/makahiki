import os
import datetime

from django.test import TestCase
from django.conf import settings
from django.core.files.images import ImageFile
from django.contrib.auth.models import User

from components.makahiki_profiles.models import Profile
from components.prizes.models import IndividualOverallPointsPrize

class IndividualOverallPointsTest(TestCase):
  def setUp(self):
    """
    Sets up a test prize for the rest of the tests.
    This prize is not saved, as some test-specific fields are not set.
    """
    image_path = os.path.join(settings.PROJECT_ROOT, "fixtures", "test_images", "test.jpg")
    image = ImageFile(open(image_path, "r"))
    self.prize = IndividualOverallPointsPrize(
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
    
    # Create test users.
    self.users = [User.objects.create_user("test%d" % i, "test@test.com") for i in range(0, 3)]
    
  def testRoundLeader(self):
    """
    Tests that we can retrieve the overall individual points leader for a round prize.
    """
    self.prize.round_name = "Round 1"
    self.prize.save()
    
    # Test one user
    profile = self.users[0].get_profile()
    top_points = Profile.objects.all().order_by("-points")[0].points
    profile.add_points(top_points + 1, datetime.datetime.today() - datetime.timedelta(minutes=1))
    profile.save()
    
    self.assertEqual(self.prize.leader(), profile, "Current prize leader is not the leading user.")
    
    # Have another user move ahead in points
    profile2 = self.users[1].get_profile()
    profile2.add_points(profile.points + 1, datetime.datetime.today())
    profile2.save()
    
    self.assertEqual(self.prize.leader(), profile2, "User 2 should be the leading profile.")
    
    # Have this user get the same amount of points, but an earlier award date.
    profile3 = self.users[2].get_profile()
    profile3.add_points(profile2.points, datetime.datetime.today() - datetime.timedelta(minutes=1))
    profile3.save()
    
    self.assertEqual(self.prize.leader(), profile2, "User 2 should still be the leading profile.")
    
    # Have the first user earn more points outside of the round.
    profile.add_points(2, datetime.datetime.today() - datetime.timedelta(days=2))
    profile.save()
    
    self.assertEqual(self.prize.leader(), profile2, "User 2 should still be the leading profile.")
    
  def testOverallLeader(self):
    """
    Tests that we can retrieve the overall individual points leader for a round prize.
    """
    self.prize.round = "Overall"
    self.prize.save()

    # Test one user
    profile = self.users[0].get_profile()
    top_points = Profile.objects.all().order_by("-points")[0].points
    profile.add_points(top_points + 1, datetime.datetime.today())
    profile.save()

    self.assertEqual(self.prize.leader(), profile, "Current prize leader is not the leading user.")
    
    # Have another user move ahead in points
    profile2 = self.users[1].get_profile()
    profile2.add_points(profile.points + 1, datetime.datetime.today())
    profile2.save()
    
    self.assertEqual(self.prize.leader(), profile2, "User 2 should be the leading profile.")
    
    # Have this user get the same amount of points, but an earlier award date.
    profile3 = self.users[2].get_profile()
    profile3.add_points(profile2.points, datetime.datetime.today() - datetime.timedelta(minutes=1))
    profile3.save()
    
    self.assertEqual(self.prize.leader(), profile2, "User 2 should still be the leading profile.")
    
  def tearDown(self):
    """
    Deletes the created image file in prizes.
    """
    settings.COMPETITION_ROUNDS = self.saved_rounds
    self.prize.delete()
    
    

