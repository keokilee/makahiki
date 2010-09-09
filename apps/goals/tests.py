import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from goals.models import EnergyGoal, EnergyGoalVote

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
    votes = results["10%"]
    
    response = self.client.post(reverse('goal_vote', args=(self.goal.pk,)), {"percent_reduction": 10}, follow=True)
    results = self.goal.get_floor_results(self.user.get_profile().floor)
    self.assertEqual(results["10%"], votes + 1, "Check that the number of results for this user's floor has changed.")