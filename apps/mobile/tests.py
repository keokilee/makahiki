import datetime

from django.test import TestCase
from django.conf import settings

from floors.models import Floor
from makahiki_profiles.models import ScoreboardEntry
from mobile import get_mobile_standings
    
class MobileRoundStandingsTestCase(TestCase):
  """Tests the generation of standings that check a user's placement in a round."""
  fixtures = ["base_data.json", "user_data.json"]

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


  def testFloorStandings(self):
    """Test that updating the points in a round changes the mobile standings."""
    entry = self.floor_entries[1] # Use second place entry.

    standings = get_mobile_standings(entry.profile.user)
    test_string = "You are #2 in points for %s for %s." % (self.floor, self.current_round)
    diff = self.floor_entries[0].points - self.floor_entries[1].points
    test_string += " Get %d more points to move to #1." % diff
    self.assertEqual(standings["floor"], test_string)
    
    entry.points += diff + 1 # Moves user to first place.
    entry.save()
    
    standings = get_mobile_standings(entry.profile.user)
    test_string = "You are #1 in points for %s for %s." % (self.floor, self.current_round)
    self.assertEqual(standings["floor"], test_string)
    
  def testOverallStandings(self):
    """Test that updating the points in a round changes the mobile standings."""
    entry = self.all_entries[1] # Use second place entry.

    standings = get_mobile_standings(entry.profile.user)
    test_string = "You are #2 in overall points for %s." % self.current_round
    diff = self.all_entries[0].points - self.all_entries[1].points
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
        

