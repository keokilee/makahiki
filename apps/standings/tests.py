import simplejson as json
import datetime

from django.test import TestCase
from django.conf import settings

from floors.models import Floor
from makahiki_profiles.models import Profile, ScoreboardEntry
from standings import get_standings_for_user
    
class FloorStandingsTest(TestCase):
  fixtures = ["base_data.json", "user_data.json"]
  
  def setUp(self):
    self.floor = Floor.objects.all()[0]
    self.profiles = self.floor.profile_set.order_by("-points", "-last_awarded_submission")
    self.count = self.profiles.count()
    
  def testStandingsFirstPlace(self):
    """Test that the standings of the first place user is correct."""
    
    json_standings = get_standings_for_user(self.profiles[0], "floor")
    decoded_standings = json.loads(json_standings)
    
    # Verify that the returned structure is correct.
    self.assertTrue(decoded_standings.has_key("title"))
    self.assertTrue(decoded_standings.has_key("info"))
    self.assertTrue(decoded_standings.has_key("myindex"))
    self.assertTrue(decoded_standings.has_key("type"))
    self.assertTrue(len(decoded_standings) == 4)
    
    # Verify that the contents are correct.
    self.assertTrue(decoded_standings["myindex"] == 0)
    self.assertTrue(len(decoded_standings["info"]) == 3)
    self.assertTrue(decoded_standings["info"][0]["rank"] == 1)
    self.assertTrue(decoded_standings["info"][2]["rank"] == self.count)
    
    first = decoded_standings["info"][0]
    second = decoded_standings["info"][1]
    self.assertTrue(first["points"] >= second["points"])
    
  def testStandingsSecondPlace(self):
    """Test that standings of the second place user is correct."""

    json_standings = get_standings_for_user(self.profiles[1], "floor")
    decoded_standings = json.loads(json_standings)
    self.assertTrue(decoded_standings["myindex"] == 1)
    self.assertTrue(len(decoded_standings["info"]) == 4)
    self.assertTrue(decoded_standings["info"][1]["rank"] == 2)
    
  def testStandingsThirdPlace(self):
    """Test that standings of the third place user is correct. This will also verify that any user in the middle is correct."""

    json_standings = get_standings_for_user(self.profiles[2], "floor")
    decoded_standings = json.loads(json_standings)
    self.assertTrue(decoded_standings["myindex"] == 2)
    self.assertTrue(len(decoded_standings["info"]) == 5)
    self.assertTrue(decoded_standings["info"][2]["rank"] == 3)
    
  def testStandingsSecondToLastPlace(self):
    """Test that standings of the second to the last user is correct."""

    json_standings = get_standings_for_user(self.profiles[self.count-2], "floor")
    decoded_standings = json.loads(json_standings)
    self.assertTrue(decoded_standings["myindex"] == 2)
    self.assertTrue(len(decoded_standings["info"]) == 4)
      
  def testStandingsLastPlace(self):
    """Test that standings of the last place user is correct."""

    json_standings = get_standings_for_user(self.profiles[self.count-1], "floor")
    decoded_standings = json.loads(json_standings)
    self.assertTrue(decoded_standings["myindex"] == 2)
    self.assertTrue(len(decoded_standings["info"]) == 3)
    self.assertTrue(decoded_standings["info"][2]["rank"] == self.count)
    
  def testAddPointsChangeStandings(self):
    """Test that adding points moves the user up."""

    # Test using the second place user.
    profile = self.profiles[1]
    json_standings = get_standings_for_user(profile, group="floor")
    decoded_standings = json.loads(json_standings)
    user_index = decoded_standings["myindex"]
    point_diff = decoded_standings["info"][0]["points"] - decoded_standings["info"][user_index]["points"]
    profile.points += point_diff + 1
    profile.save()

    json_standings = get_standings_for_user(profile, group="floor")
    decoded_standings = json.loads(json_standings)

    # Verify that user is now first.
    self.assertTrue(decoded_standings["myindex"] == 0)
    self.assertTrue(len(decoded_standings["info"]) == 3)
    
  def testChangeSubmitDateChangeStandings(self):
    """Test that tied users with different submission dates are ordered correctly."""

    # Test using the second place user.
    profile = self.profiles[1]
    json_standings = get_standings_for_user(profile, group="floor")
    decoded_standings = json.loads(json_standings)
    point_diff = decoded_standings["info"][0]["points"] - decoded_standings["info"][1]["points"]
    profile.points += point_diff # Tie for points
    profile.last_awarded_submission = datetime.datetime.today()
    profile.save()

    json_standings = get_standings_for_user(profile, group="floor")
    decoded_standings = json.loads(json_standings)

    # Verify that user is now first.
    self.assertTrue(decoded_standings["myindex"] == 0)
    self.assertTrue(len(decoded_standings["info"]) == 3)
    
class RoundStandingsTest(TestCase):
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
    self.entries = ScoreboardEntry.objects.filter(
                      profile__floor=self.floor, 
                      round_name=self.current_round
                    ).order_by("-points", "-last_awarded_submission")
    
    
  def testUpdatePointsChangesStandings(self):
    """Test that updating the points in a round changes the standings."""
    entry = self.entries[1] # Use second place entry.
    
    json_standings = get_standings_for_user(entry.profile.user, group="floor", round_name=self.current_round)
    decoded_standings = json.loads(json_standings)
    user_index = decoded_standings["myindex"]
    self.assertEqual(user_index, 1)
    point_diff = decoded_standings["info"][0]["points"] - decoded_standings["info"][user_index]["points"]
    entry.points += point_diff + 1 #Should push user to number 1.
    entry.save()
    
    json_standings = get_standings_for_user(entry.profile.user, group="floor", round_name=self.current_round)
    decoded_standings = json.loads(json_standings)
    user_index = decoded_standings["myindex"]
    self.assertEqual(user_index, 0)
    
  def testUpdateSubmissionChangesStandings(self):
    """Test that updating the submission date in a round changes the standings."""
    entry = self.entries[1] # Use second place entry.

    json_standings = get_standings_for_user(entry.profile.user, group="floor", round_name=self.current_round)
    decoded_standings = json.loads(json_standings)
    user_index = decoded_standings["myindex"]
    self.assertEqual(user_index, 1)
    entry.last_awarded_submission = datetime.datetime.today()
    entry.save()

    json_standings = get_standings_for_user(entry.profile.user, group="floor", round_name=self.current_round)
    decoded_standings = json.loads(json_standings)
    user_index = decoded_standings["myindex"]
    self.assertEqual(user_index, 0)
    
  def tearDown(self):
    """Restore the saved settings."""
    settings.COMPETITION_ROUNDS = self.saved_rounds
    
class AllStandingsTest(TestCase):
  fixtures = ["base_data.json", "user_data.json"]
  
  def setUp(self):
    self.profiles = Profile.objects.order_by("-points", "-last_awarded_submission")
    self.count = self.profiles.count()
    
  def testStandingsAllUsers(self):
    profile = self.profiles[0]
    json_standings = get_standings_for_user(profile, "all")
    decoded_standings = json.loads(json_standings)
    
    # Verify that the returned structure is correct.
    self.assertTrue(decoded_standings.has_key("title"))
    self.assertTrue(decoded_standings.has_key("info"))
    self.assertTrue(decoded_standings.has_key("myindex"))
    self.assertTrue(decoded_standings.has_key("type"))
    self.assertTrue(len(decoded_standings) == 4)
    
    # Verify that the contents are correct.
    self.assertTrue(decoded_standings["myindex"] == 0)
    self.assertTrue(len(decoded_standings["info"]) == 3)
    self.assertTrue(decoded_standings["info"][0]["rank"] == 1)
    self.assertTrue(decoded_standings["info"][2]["rank"] == self.count)
    
    first = decoded_standings["info"][0]
    second = decoded_standings["info"][1]
    self.assertTrue(first["points"] >= second["points"])
    