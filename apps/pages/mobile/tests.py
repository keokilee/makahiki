import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings

from components.floors.models import Floor
from components.makahiki_profiles.models import ScoreboardEntry, Profile
from pages.mobile import get_mobile_standings
    
class MobileRoundStandingsTestCase(TestCase):
  """Tests the generation of standings that check a user's placement in a round."""
  fixtures = ["base_floors.json", "test_users.json"]

  def setUp(self):
    """Set the competition settings to the current date for testing."""
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

    self.floor = Floor.objects.all()[0]
    self.floor_entries = ScoreboardEntry.objects.filter(
                            profile__floor=self.floor, 
                            round_name=self.current_round
                         ).order_by("-points", "-last_awarded_submission")
                    
    self.all_entries = ScoreboardEntry.objects.filter(
                          round_name=self.current_round,
                       ).order_by("-points", "-last_awarded_submission")


  # def testFloorStandings(self):
  #   """Test that updating the points in a round changes the mobile standings."""
  #   entry = self.floor_entries[1] # Use second place entry.
  # 
  #   standings = get_mobile_standings(entry.profile.user)
  #   test_string = "You are #2 in points for %s for %s." % (self.floor, self.current_round)
  #   diff = self.floor_entries[0].points - self.floor_entries[1].points
  #   if diff == 0:
  #     diff = 1
  #     test_string += " Get %d more point to move to #1." % diff
  #   else:
  #     test_string += " Get %d more points to move to #1." % diff
  #   self.assertEqual(standings["floor"], test_string)
  #   
  #   entry.points += diff + 1 # Moves user to first place.
  #   entry.save()
  #   
  #   standings = get_mobile_standings(entry.profile.user)
  #   test_string = "You are #1 in points for %s for %s." % (self.floor, self.current_round)
  #   self.assertEqual(standings["floor"], test_string)
    
  def testOverallStandings(self):
    """Test that updating the points in a round changes the mobile standings."""
    entry = self.all_entries[1] # Use second place entry.

    standings = get_mobile_standings(entry.profile.user)
    test_string = "You are #2 in overall points for %s." % self.current_round
    diff = self.all_entries[0].points - self.all_entries[1].points
    if diff < 2:
      test_string += " Get 1 more point to move to #1."
    else:
      test_string += " Get %d more points to move to #1." % diff
    self.assertEqual(standings["overall"], test_string)

    entry.points += diff + 1 # Moves user to first place.
    entry.save()

    standings = get_mobile_standings(entry.profile.user)
    test_string = "You are #1 in overall points for %s." % self.current_round
    self.assertEqual(standings["overall"], test_string)
    
  def tearDown(self):
    """Restore the saved settings."""
    settings.COMPETITION_ROUNDS = self.saved_rounds
    
class MobileOverallStandingsTestCase(TestCase):
  """Tests the generation of standings that check a user's placement in a round."""
  fixtures = ["base_floors.json", "test_users.json"]

  def setUp(self):
    """Set the competition settings to the current date for testing."""
    self.saved_rounds = settings.COMPETITION_ROUNDS
    self.current_round = "Round 1"
    start = datetime.date.today() - datetime.timedelta(days=14)
    end = start + datetime.timedelta(days=7)

    settings.COMPETITION_ROUNDS = {
      "Round 1" : {
        "start": start.strftime("%Y-%m-%d"),
        "end": end.strftime("%Y-%m-%d"),
      },
    }

    self.floor = Floor.objects.all()[0]
    self.floor_profiles = Profile.objects.filter(
                            floor=self.floor, 
                         ).order_by("-points", "-last_awarded_submission")

    self.all_profiles = Profile.objects.order_by("-points", "-last_awarded_submission")


  def testFloorStandings(self):
    """Test that updating the overall points changes the mobile standings."""
    profile = self.floor_profiles[1] # Use second place profile.

    standings = get_mobile_standings(profile.user)
    test_string = "You are #2 in points for %s in the competition." % (self.floor)
    diff = self.floor_profiles[0].points - self.floor_profiles[1].points
    if diff == 0:
      diff = 1
      test_string += " Get %d more point to move to #1." % diff
    else:
      test_string += " Get %d more points to move to #1." % diff
    self.assertEqual(standings["floor"], test_string)

    profile.points += diff + 1 # Moves user to first place.
    profile.save()

    standings = get_mobile_standings(profile.user)
    test_string = "You are #1 in points for %s in the competition." % self.floor
    self.assertEqual(standings["floor"], test_string)

  def testOverallStandings(self):
    """Test that updating the overall points changes the mobile standings."""
    profile = self.all_profiles[1] # Use second place entry.

    standings = get_mobile_standings(profile.user)
    test_string = "You are #2 in overall points in the competition."
    diff = self.all_profiles[0].points - self.all_profiles[1].points
    if diff == 0:
      diff = 1
      test_string += " Get %d more point to move to #1." % diff
    else:
      test_string += " Get %d more points to move to #1." % diff
    
    self.assertEqual(standings["overall"], test_string)

    profile.points += diff + 1 # Moves user to first place.
    profile.save()

    standings = get_mobile_standings(profile.user)
    test_string = "You are #1 in overall points in the competition."
    self.assertEqual(standings["overall"], test_string)

  def tearDown(self):
    """Restore the saved settings."""
    settings.COMPETITION_ROUNDS = self.saved_rounds

class MobileFunctionalTestCase(TestCase):
  def testIndex(self):
    """Check that we can load the index."""
    response = self.client.get(reverse("mobile_index"))
    self.failUnlessEqual(response.status_code, 200)