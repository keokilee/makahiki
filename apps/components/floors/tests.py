import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Sum, Max

from components.floors.models import Dorm, Floor
from components.makahiki_profiles.models import ScoreboardEntry

class FloorsUnitTestCase(TestCase):
  def setUp(self):
    self.dorm = Dorm(name="Test dorm")
    self.dorm.save()
    self.test_floor = Floor(number="A", dorm=self.dorm)
    self.test_floor.save()
    
  def testOverallPoints(self):
    """Check that retrieving the points for the floor is correct."""
    # Create a test user.
    user = User(username="test_user", password="test_password")
    user.save()
    user_points = 10
    user.get_profile().floor = self.test_floor
    
    self.assertEqual(self.test_floor.points(), 0, "Check that the floor does not have any points yet.")
    
    user.get_profile().add_points(user_points, datetime.datetime.today())
    user.get_profile().save()
    
    self.assertEqual(self.test_floor.points(), user_points, "Check that the number of points are equal for one user.")
    
    # Create another test user and check again.
    user = User(username="test_user1", password="test_password")
    user.save()
    user.get_profile().floor = self.test_floor
    user.get_profile().add_points(user_points, datetime.datetime.today())
    user.get_profile().save()
    
    self.assertEqual(self.test_floor.points(), 2*user_points, "Check that the number of points are equal for two users.")
    
  def testPointsInRound(self):
    """Tests that we can accurately compute the amount of points in a round."""
    # Save the round information and set up a test round.
    saved_rounds = settings.COMPETITION_ROUNDS
    current_round = "Round 1"
    start = datetime.date.today()
    end = start + datetime.timedelta(days=7)

    settings.COMPETITION_ROUNDS = {
      "Round 1" : {
        "start": start.strftime("%Y-%m-%d"),
        "end": end.strftime("%Y-%m-%d"),
      },
    }
    
    user = User(username="test_user", password="test_password")
    user.save()
    profile = user.get_profile()
    profile.floor = self.test_floor
    profile.save()
    
    self.assertEqual(self.test_floor.current_round_points(), 0, "Check that the floor does not have any points yet.")
    
    profile.add_points(10, datetime.datetime.today())
    profile.save()
    
    self.assertEqual(self.test_floor.current_round_points(), 10, "Check that the number of points are correct in this round.")
    
    profile.add_points(10, datetime.datetime.today() - datetime.timedelta(days=3))
    profile.save()
    
    self.assertEqual(self.test_floor.current_round_points(), 10, "Check that the number of points did not change.")
    
    # Restore saved rounds.
    settings.COMPETITION_ROUNDS = saved_rounds
    
  def testOverallRankWithPoints(self):
    """Check that calculating the rank is correct based on point value."""
    # Create a test user.
    user = User(username="test_user", password="test_password")
    user.save()
    user_points = 10
    user.get_profile().floor = self.test_floor
    
    # Test the floor is ranked last if they haven't done anything yet.
    floor_rank = Floor.objects.annotate(
        floor_points=Sum("profile__points"),
        last_awarded_submission=Max("profile__last_awarded_submission")
    ).filter(floor_points__gt=self.test_floor.points).count() + 1
    self.assertEqual(self.test_floor.rank(), floor_rank, "Check the floor is ranked last.")
    
    user.get_profile().add_points(user_points, datetime.datetime.today())
    user.get_profile().save()

    self.assertEqual(self.test_floor.rank(), 1, "Check the floor is now ranked number 1.")

    # Create a test user on a different floor.
    test_floor2 = Floor(number="B", dorm=self.dorm)
    test_floor2.save()
    
    user2 = User(username="test_user1", password="test_password")
    user2.save()
    user2.get_profile().floor = test_floor2
    user2.get_profile().add_points(user_points + 1, datetime.datetime.today())
    user2.get_profile().save()
    
    self.assertEqual(self.test_floor.rank(), 2, "Check that the floor is now ranked number 2.")
    
  def testRoundRank(self):
    """Check that the rank calculation is correct for the current round."""
    # Save the round information and set up a test round.
    saved_rounds = settings.COMPETITION_ROUNDS
    current_round = "Round 1"
    start = datetime.date.today()
    end = start + datetime.timedelta(days=7)

    settings.COMPETITION_ROUNDS = {
      "Round 1" : {
        "start": start.strftime("%Y-%m-%d"),
        "end": end.strftime("%Y-%m-%d"),
      },
    }
    
    # Create a test user.
    user = User(username="test_user", password="test_password")
    user.save()
    user_points = 10
    user.get_profile().floor = self.test_floor
    user.get_profile().save()
    
    ScoreboardEntry.objects.values("profile__floor").filter(
        round_name=current_round
    ).annotate(
        floor_points=Sum("points"),
        last_awarded=Max("last_awarded_submission")
    ).filter(floor_points__gt=self.test_floor.points).count() + 1
    self.assertEqual(self.test_floor.current_round_rank(), 1, "Check the calculation works even if there's no submission.")
    
    user.get_profile().add_points(user_points, datetime.datetime.today())
    user.get_profile().save()
    self.assertEqual(self.test_floor.current_round_rank(), 1, "Check the floor is now ranked number 1.")
    
    test_floor2 = Floor(number="B", dorm=self.dorm)
    test_floor2.save()
    
    user2 = User(username="test_user1", password="test_password")
    user2.save()
    user2.get_profile().floor = test_floor2
    user2.get_profile().add_points(user_points + 1, datetime.datetime.today())
    user2.get_profile().save()
    
    self.assertEqual(self.test_floor.current_round_rank(), 2, "Check the floor is now ranked number 2.")
    
    user.get_profile().add_points(user_points, datetime.datetime.today() - datetime.timedelta(days=3))
    user.get_profile().save()
    
    self.assertEqual(self.test_floor.current_round_rank(), 2, "Check the floor is still ranked number 2.")
    
    settings.COMPETITION_ROUNDS = saved_rounds
    
  def testOverallRankWithSubmissionDate(self):
    """Check that rank calculation is correct in the case of ties."""
    # Create a test user.
    user = User(username="test_user", password="test_password")
    user.save()
    user_points = 10
    user.get_profile().floor = self.test_floor
    user.get_profile().add_points(user_points, datetime.datetime.today() - datetime.timedelta(days=3))
    user.get_profile().save()

    # Create a test user on a different floor.
    test_floor2 = Floor(number="B", dorm=self.dorm)
    test_floor2.save()

    user = User(username="test_user1", password="test_password")
    user.save()
    user.get_profile().floor = test_floor2
    user.get_profile().add_points(user_points, datetime.datetime.today())
    user.get_profile().save()

    self.assertEqual(self.test_floor.rank(), 2, "Check that the floor is ranked second.")