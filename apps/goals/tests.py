import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.conf import settings

from goals.models import EnergyGoal, EnergyGoalVote, FloorEnergyGoal
from goals import generate_floor_goals
from floors.models import Floor
from makahiki_profiles.models import Profile, ScoreboardEntry

class EnergyGoalUnitTestCase(TestCase):
  def testGetCurrentGoal(self):
    """Tests that we can retrieve the current goal."""
    current_goal = EnergyGoal.get_current_goal()
    self.assertTrue(current_goal is None, "Check that there is no current goal.")
    
    start = datetime.date.today() - datetime.timedelta(days=1)
    voting_end = start + datetime.timedelta(days=3)
    end = start + datetime.timedelta(days=7)
    goal = EnergyGoal(
          start_date=start,
          voting_end_date=voting_end,
          end_date=end,
    )
    goal.save()
    
    current_goal = EnergyGoal.get_current_goal()
    self.assertEqual(current_goal, goal, "Check that we can retrieve the current goal.")
    
  def testInVotingPeriod(self):
    """Tests that the in voting method works."""
    start = datetime.date.today() - datetime.timedelta(days=2)
    voting_end = start + datetime.timedelta(days=3)
    end = start + datetime.timedelta(days=7)
    goal = EnergyGoal(
          start_date=start,
          voting_end_date=voting_end,
          end_date=end,
    )
    goal.save()
    
    self.assertTrue(goal.in_voting_period(), "Check that the goal is currently in the voting period.")
    goal.voting_end_date = datetime.date.today() - datetime.timedelta(days=1)
    goal.save()
    
    self.assertFalse(goal.in_voting_period(), "Check that the goal is now not in the voting period.")
    
  def testUserCanVote(self):
    """Tests that this is toggled when the user submits a vote."""
    user = User(username="test_user", password="changeme")
    user.save()
    
    start = datetime.date.today() - datetime.timedelta(days=2)
    voting_end = start + datetime.timedelta(days=3)
    end = start + datetime.timedelta(days=7)
    goal = EnergyGoal(
          start_date=start,
          voting_end_date=voting_end,
          end_date=end,
    )
    goal.save()
    
    self.assertTrue(goal.user_can_vote(user), "Check that the user has not submitted a vote.")
    vote = EnergyGoalVote(user=user, goal=goal, percent_reduction=10)
    vote.save()
    
    self.assertFalse(goal.user_can_vote(user), "Check that the user has now submitted a vote.")
    
class EnergyGoalHelperTestCase(TestCase):
  fixtures = ["base_data.json", "user_data.json"]
  
  def testGenerateFloorGoals(self):
    """Tests the generation of floor goals."""
    start = datetime.date.today() - datetime.timedelta(days=2)
    voting_end = datetime.date.today() + datetime.timedelta(days=1)
    end = start + datetime.timedelta(days=7)
    goal = EnergyGoal(
          start_date=start,
          voting_end_date=voting_end,
          end_date=end,
    )
    goal.save()
    
    # Test that this goal does not generate any floor goals because the voting period is not up.
    generate_floor_goals()
    for floor in Floor.objects.all():
      self.assertEqual(floor.floorenergygoal_set.count(), 0, "Test that no goals are created yet.")
    
    goal.voting_end_date = datetime.date.today()
    goal.save()
    
    # Create a test vote for a user.
    user = User.objects.get(username="user")
    vote = EnergyGoalVote(user=user, goal=goal, percent_reduction=10)
    vote.save()
    
    # Generate floor goals.
    generate_floor_goals()
    for floor in Floor.objects.all():
      floor_goal = FloorEnergyGoal.objects.get(floor=floor, goal=goal)
      
      # Our test user's floor should have a 10 percent reduction goal.
      if floor == user.get_profile().floor:
        self.assertEqual(floor_goal.percent_reduction, 10, "Check that test user's vote counts.")
      else:
        self.assertEqual(floor_goal.percent_reduction, 0, "Check that default goal is 0.")
        
  def testGeneratingMultipleGoals(self):
    """
    Tests that generate_floor_goals does not generate multiple goals and that multiple goals cannot be created.
    """
    start = datetime.date.today() - datetime.timedelta(days=2)
    voting_end = datetime.date.today()
    end = start + datetime.timedelta(days=7)
    goal = EnergyGoal(
          start_date=start,
          voting_end_date=voting_end,
          end_date=end,
    )
    goal.save()
    
    # Try executing twice to see if an exception occurs.
    generate_floor_goals()
    try:
      generate_floor_goals()
    except ValidationError:
      self.fail("generate_floor_goals should not cause an exception.")
      
    for floor in Floor.objects.all():
      self.assertEqual(floor.floorenergygoal_set.count(), 1, "Check that there is only one goal.")

class EnergyGoalFunctionalTestCase(TestCase):
  fixtures = ["base_data.json", "user_data.json"]
  
  def setUp(self):
    """Create a test goal and log in the user."""
    self.user = User.objects.get(username="user")
    self.client.post('/account/login/', {"username": self.user.username, "password": "changeme", "remember": False})
    
    start = datetime.date.today() - datetime.timedelta(days=2)
    voting_end = start + datetime.timedelta(days=3)
    end = start + datetime.timedelta(days=7)
    self.goal = EnergyGoal(
          start_date=start,
          voting_end_date=voting_end,
          end_date=end,
    )
    self.goal.save()
    
  def testUserVoting(self):
    """Check that the user goal box appears."""
    response = self.client.get(reverse("profile_detail", args=(self.user.get_profile().pk,)))
    goal_dict = response.context["energy_goal"]
    self.assertTrue(goal_dict.has_key("form"), "Check that the context dictionary contains the voting form.")
    
    response = self.client.post(reverse('goal_vote', args=(self.goal.pk,)), {"percent_reduction": 10}, follow=True)
    goal_dict = response.context["energy_goal"]
    self.assertTrue(goal_dict["form"] is None, "Check that the context no longer contains a voting form.")
    
  def testUserResults(self):
    """Check that the results of the vote are accurate."""
    # Save the current votes.
    results = self.goal.get_floor_results(self.user.get_profile().floor)
    votes = 0
    for result in results:
      if result["percent_reduction"] == 10:
        votes = result["votes"]
        break
    
    response = self.client.post(reverse('goal_vote', args=(self.goal.pk,)), {"percent_reduction": 10}, follow=True)
    results = self.goal.get_floor_results(self.user.get_profile().floor)
    
    for result in results:
      if result["percent_reduction"] == 10:
        self.assertEqual(result["votes"], votes + 1, "Check that the number of results for this user's floor has changed.")
        return
        
    self.fail("Could not find the vote matching the percent reduction.")
    
class FloorEnergyGoalUnitTestCase(TestCase):
  fixtures = ["base_data.json", "user_data.json"]
  
  def setUp(self):
    self.saved_rounds = settings.COMPETITION_ROUNDS
    self.current_round = "Round 1"
    start = datetime.date.today() - datetime.timedelta(days=7)
    end = start + datetime.timedelta(days=6)

    settings.COMPETITION_ROUNDS = {
      "Round 1" : {
        "start": start.strftime("%Y-%m-%d"),
        "end": end.strftime("%Y-%m-%d"),
      },
    }
    
    start = datetime.date.today() - datetime.timedelta(days=7)
    voting_end = start + datetime.timedelta(days=3)
    end = start + datetime.timedelta(days=6)
    self.goal = EnergyGoal(
          start_date=start,
          voting_end_date=voting_end,
          end_date=end,
          point_conversion=1.0,
    )
    self.goal.save()
    
  def testRoundPoints(self):
    """Test that we can assign points to a round when the goal ends at the same time."""
    user = User.objects.get(username="user")
    profile = user.get_profile()
    floor = profile.floor
    overall_points = profile.points
    entry, created = ScoreboardEntry.objects.get_or_create(profile=profile, round_name=self.current_round)
    round_points = entry.points
    
    floor_goal = FloorEnergyGoal(floor=floor, goal=self.goal, percent_reduction=10, completed=True)
    floor_goal.save()
    
    self.assertTrue(floor_goal.awarded, "Check that the goal was awarded.")
    test_profile = Profile.objects.get(user=user)
    self.assertEqual(test_profile.points, overall_points + 10, "Check that points are awarded overall.")
    entry = ScoreboardEntry.objects.get(profile=user.get_profile(), round_name=self.current_round)
    self.assertEqual(entry.points, round_points + 10, "Check that points are awarded for this round.")
    
  def tearDown(self):
    """Restore the saved settings."""
    settings.COMPETITION_ROUNDS = self.saved_rounds