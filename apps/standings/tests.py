import simplejson as json
import datetime

from django.test import TestCase
from django.conf import settings
from django.db.models import Sum, Max
from django.contrib.auth.models import User

from floors.models import Dorm, Floor
from makahiki_profiles.models import Profile, ScoreboardEntry
from standings import get_standings_for_user, get_floor_standings, get_individual_standings, MAX_INDIVIDUAL_STANDINGS
    
class UserFloorStandingsTest(TestCase):
  """Tests the generation of standings that check a user's placement in a floor."""
  fixtures = ["base_data.json", "user_data.json"]
  
  def setUp(self):
    self.floor = Floor.objects.all()[0]
    self.profiles = self.floor.profile_set.order_by("-points", "-last_awarded_submission")
    self.count = self.profiles.count()
    
  def testUserStandingsFirstPlace(self):
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
    
  def testUserStandingsSecondPlace(self):
    """Test that standings of the second place user is correct."""

    json_standings = get_standings_for_user(self.profiles[1], "floor")
    decoded_standings = json.loads(json_standings)
    self.assertTrue(decoded_standings["myindex"] == 1)
    self.assertTrue(len(decoded_standings["info"]) == 4)
    self.assertTrue(decoded_standings["info"][1]["rank"] == 2)
    
  def testUserStandingsThirdPlace(self):
    """Test that standings of the third place user is correct. This will also verify that any user in the middle is correct."""

    json_standings = get_standings_for_user(self.profiles[2], "floor")
    decoded_standings = json.loads(json_standings)
    self.assertTrue(decoded_standings["myindex"] == 2)
    self.assertTrue(len(decoded_standings["info"]) == 5)
    self.assertTrue(decoded_standings["info"][2]["rank"] == 3)
    
  def testUserStandingsSecondToLastPlace(self):
    """Test that standings of the second to the last user is correct."""

    json_standings = get_standings_for_user(self.profiles[self.count-2], "floor")
    decoded_standings = json.loads(json_standings)
    self.assertTrue(decoded_standings["myindex"] == 2)
    self.assertTrue(len(decoded_standings["info"]) == 4)
      
  def testUserStandingsLastPlace(self):
    """Test that standings of the last place user is correct."""

    json_standings = get_standings_for_user(self.profiles[self.count-1], "floor")
    decoded_standings = json.loads(json_standings)
    self.assertTrue(decoded_standings["myindex"] == 2)
    self.assertTrue(len(decoded_standings["info"]) == 3)
    self.assertTrue(decoded_standings["info"][2]["rank"] == self.count)
    
  def testUserAddPointsChangeStandings(self):
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
    
  def testUserChangeSubmitDateChangeStandings(self):
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
    
class UserRoundStandingsTest(TestCase):
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
    self.entries = ScoreboardEntry.objects.filter(
                      profile__floor=self.floor, 
                      round_name=self.current_round
                    ).order_by("-points", "-last_awarded_submission")
    
    
  def testUpdateUserPointsChangesStandings(self):
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
    
  def testUpdateUserSubmissionChangesStandings(self):
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
    
class UserAllStandingsTest(TestCase):
  """Tests the generation of standings that check a user's placement across all users."""
  fixtures = ["base_data.json", "user_data.json"]
  
  def setUp(self):
    self.profiles = Profile.objects.order_by("-points", "-last_awarded_submission")
    self.count = self.profiles.count()
    
  def testStandingsAllUsers(self):
    """Tests the overall standings for all users."""
    profile = self.profiles[0]
    json_standings = get_standings_for_user(profile, group="all")
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
    
class UserRoundStandingsTest(TestCase):
  """Tests the generation of standings that check a user's placement in a round across all users."""
  
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
    
    self.entries = ScoreboardEntry.objects.filter(
                      round_name=self.current_round,
                    ).order_by("-points", "-last_awarded_submission")
    self.count = self.entries.count()
                    
  def testRoundOverallStandings(self):
    """Tests the overall standings for all users in a round."""
    
    # Use first entry.
    entry = self.entries[0]
    json_standings = get_standings_for_user(entry.profile, group="all", round_name=self.current_round)
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
                    
  def tearDown(self):
    """Restore the saved settings."""
    settings.COMPETITION_ROUNDS = self.saved_rounds
    
class FloorStandingsTest(TestCase):
  """Tests that check the generated standings for floors."""
  
  fixtures = ["base_data.json", "user_data.json"]
  
  def setUp(self):
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
    
    # Backup previous setting for the floor label.
    if settings.COMPETITION_GROUP_NAME:
      self.saved_name = settings.COMPETITION_GROUP_NAME
    
    settings.COMPETITION_GROUP_NAME = "Lounge"
    self.title_prefix = "Lounge vs. Lounge"
    
    # Grab the last place floor as the test floor.
    self.test_floor = Floor.objects.annotate(
                          points=Sum("profile__points"), 
                          last_awarded_submission=Max("profile__last_awarded_submission")
                      ).order_by("points", "last_awarded_submission")[0]
                      
  def testFloorStandingsOverall(self):
    json_standings = get_floor_standings()
    decoded_standings = json.loads(json_standings)
    
    # Verify that the returned structure is correct.
    self.assertTrue(decoded_standings.has_key("title"))
    self.assertTrue(decoded_standings.has_key("info"))
    
    # Verify that the contents are correct.
    self.assertEqual(len(decoded_standings["info"]), Floor.objects.count(), 
                    "Test that the correct number of floors is generated.")
    self.assertEqual(decoded_standings["title"], "%s: Overall" % self.title_prefix,
                    "Test that correct title is generated.")
    
    first = decoded_standings["info"][0]
    second = decoded_standings["info"][1]
    self.assertTrue(first["points"] >= second["points"])
    
  def testFloorStandingsForRound(self):
    """Test the standings for a round."""
    json_standings = get_floor_standings(round_name=self.current_round)
    decoded_standings = json.loads(json_standings)

    # Verify that the returned structure is correct.
    self.assertTrue(decoded_standings.has_key("title"))
    self.assertTrue(decoded_standings.has_key("info"))
    
    # Verify that the contents are correct.
    self.assertEqual(len(decoded_standings["info"]), Floor.objects.count())
    self.assertEqual(decoded_standings["title"], "%s: %s" % (self.title_prefix, self.current_round),
                    "Test that correct title is generated.")
    
    first = decoded_standings["info"][0]
    second = decoded_standings["info"][1]
    self.assertTrue(first["points"] >= second["points"])
    
  def testFloorStandingsWithDorm(self):
    """Test getting the standings for a dorm."""
    dorm = Dorm.objects.all()[0]
    json_standings = get_floor_standings(dorm=dorm,)
    decoded_standings = json.loads(json_standings)
    
    # Verify that the returned structure is correct.
    self.assertTrue(decoded_standings.has_key("title"))
    self.assertTrue(decoded_standings.has_key("info"))
    
    # Verify that the contents are correct.
    self.assertEqual(len(decoded_standings["info"]), dorm.floor_set.count(), 
                    "Test that the correct number of floors is generated.")
    self.assertEqual(decoded_standings["title"], "%s: Overall" % dorm.name,
                    "Test that correct title is generated.")
    
    first = decoded_standings["info"][0]
    second = decoded_standings["info"][1]
    self.assertTrue(first["points"] >= second["points"])
    
  def testAddPointsChangeStandings(self):
    json_standings = get_floor_standings()
    decoded_standings = json.loads(json_standings)
    
    # Save first place label.
    first_label = decoded_standings["info"][0]["label"]
                        
    floor_points = self.test_floor.points
    point_diff = decoded_standings["info"][0]["points"] - floor_points
    profile = self.test_floor.profile_set.all()[0]
    profile.points += point_diff + 1 # Should move this floor ahead.
    profile.save()
    
    json_standings = get_floor_standings()
    decoded_standings = json.loads(json_standings)
    self.assertEqual(decoded_standings["info"][1]["label"], first_label, 
                        "Test that the original first place floor is now second.")
    self.assertEqual(decoded_standings["info"][0]["points"], floor_points + point_diff + 1,
                      "Test that the points were updated.")
                      
  def testChangeSubmissionChangesStandings(self):
    json_standings = get_floor_standings()
    decoded_standings = json.loads(json_standings)

    # Save first place label.
    first_label = decoded_standings["info"][0]["label"]

    floor_points = self.test_floor.points
    point_diff = decoded_standings["info"][0]["points"] - floor_points
    profile = self.test_floor.profile_set.all()[0]
    profile.points += point_diff # Should move this floor into a tie.
    profile.last_awarded_submission = datetime.datetime.today()
    profile.save()

    json_standings = get_floor_standings()
    decoded_standings = json.loads(json_standings)
    self.assertEqual(decoded_standings["info"][1]["label"], first_label, 
                        "Test that the original first place floor is now second.")
    self.assertEqual(decoded_standings["info"][0]["points"], floor_points + point_diff,
                        "Test that the points were updated.")
    
    
  def tearDown(self):
    """Restore the saved settings."""
    
    settings.COMPETITION_ROUNDS = self.saved_rounds
    
    if self.saved_name:
      settings.COMPETITION_GROUP_NAME = self.saved_name
    
class IndividualStandingsTest(TestCase):
  """Tests that check the generated standings for individuals (not based on a user)."""

  fixtures = ["base_data.json", "user_data.json"]

  def setUp(self):
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
    
    # Backup previous setting for the floor label.
    if settings.COMPETITION_GROUP_NAME:
      self.saved_name = settings.COMPETITION_GROUP_NAME
    
    settings.COMPETITION_GROUP_NAME = "Lounge"
    self.title_prefix = "Lounge vs. Lounge"

    # Grab the last place user as the test user.
    self.test_user = Profile.objects.order_by("points", "last_awarded_submission")[0]
    
  def testUserStandingsOverall(self):
    json_standings = get_individual_standings()
    decoded_standings = json.loads(json_standings)

    # Verify that the returned structure is correct.
    self.assertTrue(decoded_standings.has_key("title"))
    self.assertTrue(decoded_standings.has_key("info"))

    # Verify that the contents are correct.
    self.assertEqual(len(decoded_standings["info"]), MAX_INDIVIDUAL_STANDINGS, 
                    "Test that the correct number of individuals is generated.")
    self.assertEqual(decoded_standings["title"], "%s: Overall" % self.title_prefix,
                    "Test that correct title is generated.")

    first = decoded_standings["info"][0]
    second = decoded_standings["info"][1]
    self.assertTrue(first["points"] >= second["points"])
    
  def testUserStandingsForRound(self):
    """Test the standings for a round."""
    json_standings = get_individual_standings(round_name=self.current_round)
    decoded_standings = json.loads(json_standings)

    # Verify that the returned structure is correct.
    self.assertTrue(decoded_standings.has_key("title"))
    self.assertTrue(decoded_standings.has_key("info"))

    # Verify that the contents are correct.
    self.assertEqual(decoded_standings["title"], "%s: %s" % (self.title_prefix, self.current_round),
                    "Test that correct title is generated.")

    first = decoded_standings["info"][0]
    second = decoded_standings["info"][1]
    self.assertTrue(first["points"] >= second["points"])

  def testFloorStandingsWithDorm(self):
    """Test getting the standings for a dorm."""
    dorm = Dorm.objects.all()[0]
    json_standings = get_individual_standings(dorm=dorm,)
    decoded_standings = json.loads(json_standings)

    # Verify that the returned structure is correct.
    self.assertTrue(decoded_standings.has_key("title"))
    self.assertTrue(decoded_standings.has_key("info"))

    # Verify that the contents are correct.
    self.assertEqual(decoded_standings["title"], "%s: Overall" % dorm.name,
                    "Test that correct title is generated.")

    first = decoded_standings["info"][0]
    second = decoded_standings["info"][1]
    self.assertTrue(first["points"] >= second["points"])

  def testAddPointsChangeStandings(self):
    json_standings = get_floor_standings()
    decoded_standings = json.loads(json_standings)
    # Save label of first place user.
    first_label = decoded_standings["info"][0]["label"]
    
    point_diff = decoded_standings["info"][0]["points"] - self.test_user.points
    self.test_user.points += point_diff + 1 # Should move this floor ahead.
    self.test_user.save()

    json_standings = get_floor_standings()
    decoded_standings = json.loads(json_standings)
    self.assertEqual(decoded_standings["info"][1]["label"], first_label, 
                      "Test that the original first place floor is now second.")
                      
  def testChangeSubmissionChangesStandings(self):
    json_standings = get_floor_standings()
    decoded_standings = json.loads(json_standings)
    first_label = decoded_standings["info"][0]["label"]

    point_diff = decoded_standings["info"][0]["points"] - self.test_user.points
    self.test_user.points += point_diff # Should move this user into a tie.
    self.test_user.last_awarded_submission = datetime.datetime.today()
    self.test_user.save()

    json_standings = get_floor_standings()
    decoded_standings = json.loads(json_standings)
    self.assertEqual(decoded_standings["info"][1]["label"], first_label, 
                      "Test that the former 1st place floor is now second.")

  def tearDown(self):
    """Restore the saved settings."""
    settings.COMPETITION_ROUNDS = self.saved_rounds
    
    if self.saved_name:
      settings.COMPETITION_GROUP_NAME = self.saved_name
    
class StandingsFunctionalTest(TestCase):
  fixtures = ["base_data.json", "user_data.json"]
  
  def testDefaultView(self):
    """Test that we can load the default stadings view."""
    
    import settings
    
    # Backup previous setting.
    if settings.COMPETITION_GROUP_NAME:
      self.saved_name = settings.COMPETITION_GROUP_NAME
    
    settings.COMPETITION_GROUP_NAME = "Lounge"
    
    response = self.client.get("/standings/")
    self.assertNotContains(response, "Floor vs. Floor")
    self.assertNotContains(response, "Floor Points")
    self.assertContains(response, "Lounge vs. Lounge")
    self.assertContains(response, "Lounge Points")
    
    # Restore setting.
    if self.saved_name:
      settings.COMPETITION_GROUP_NAME = self.saved_name
      
  def testProfileView(self):
    """Test that we can load the profile view and that the correct settings are in place."""
    
    import settings
    
    # Backup previous setting.
    if settings.COMPETITION_GROUP_NAME:
      self.saved_name = settings.COMPETITION_GROUP_NAME
    
    settings.COMPETITION_GROUP_NAME = "Lounge"
    
    user = User.objects.get(username="user")
    self.client.post('/account/login/', {"username": user.username, "password": "changeme", "remember": False})
    
    # Go to user's profile page and check for the floor text.
    profile = user.get_profile()
    response = self.client.get('/profiles/profile/%s/' % user.pk)
    self.assertNotContains(response, profile.floor.dorm.name + ": Floor")
    self.assertNotContains(response, "<b>Floor</b>")
    self.assertNotContains(response, "My Floor")
    self.assertContains(response, profile.floor.dorm.name + ": Lounge " + profile.floor.number)
    self.assertContains(response, "<b>Lounge</b>")
    self.assertContains(response, "My Lounge")
    
    # Restore setting.
    if self.saved_name:
      settings.COMPETITION_GROUP_NAME = self.saved_name
    