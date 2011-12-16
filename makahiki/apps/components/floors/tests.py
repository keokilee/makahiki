import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Sum, Max

from components.floors.models import Dorm, Floor
from components.makahiki_profiles.models import ScoreboardEntry

class DormUnitTestCase(TestCase):
  def setUp(self):
    self.dorms = [Dorm(name="Test Dorm %d" % i) for i in range(0, 2)]
    map(lambda d: d.save(), self.dorms)
    
    self.floors = [Floor(number=str(i), dorm=self.dorms[i % 2]) for i in range(0, 4)]
    map(lambda f: f.save(), self.floors)
    
    self.users = [User.objects.create_user("test%d" % i, "test@test.com") for i in range(0, 4)]
    
    # Assign users to floors.
    for index, user in enumerate(self.users):
      user.get_profile().floor = self.floors[index % 4]
      user.get_profile().save()
      
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
    
  def testFloorPointsInRound(self):
    """
    Tests calculating the floor points leaders in a round.
    """
    profile = self.users[0].get_profile()
    profile.add_points(10, datetime.datetime.today() - datetime.timedelta(minutes=1), "test")
    profile.save()
    
    self.assertEqual(self.dorms[0].floor_points_leaders(round_name=self.current_round)[0], profile.floor, 
        "The user's floor is not leading in the prize.")
        
    # Test that a user in a different floor but same dorm changes the leader for the original user.
    profile2 = self.users[2].get_profile()
    profile2.add_points(profile.points + 1, datetime.datetime.today() - datetime.timedelta(minutes=1), "test")
    profile2.save()
    
    self.assertEqual(self.dorms[0].floor_points_leaders(round_name=self.current_round)[0], profile2.floor, 
        "The user's floor should have changed.")
        
    # Test that adding points outside of the round does not affect the leaders.
    profile.add_points(10, datetime.datetime.today() - datetime.timedelta(days=2), "test")
    profile.save()
    
    self.assertEqual(self.dorms[0].floor_points_leaders(round_name=self.current_round)[0], profile2.floor, 
        "The leader of the floor should not change.")
        
    # Test that adding points to a user in a different dorm does not change affect these standings.
    profile1 = self.users[1].get_profile()
    profile1.add_points(profile.points + 1, datetime.datetime.today() - datetime.timedelta(minutes=1), "test")
    profile1.save()
    
    self.assertEqual(self.dorms[0].floor_points_leaders(round_name=self.current_round)[0], profile2.floor, 
        "The leader of the floor should not change.")
    self.assertEqual(self.dorms[1].floor_points_leaders(round_name=self.current_round)[0], profile1.floor, 
        "The leader in the second dorm should be profile1's floor.")
        
    # Test that a tie is handled properly.
    profile.add_points(1, datetime.datetime.today(), "test")
    profile.save()
    
    self.assertEqual(self.dorms[0].floor_points_leaders(round_name=self.current_round)[0], profile.floor, 
        "The leader of the floor should have changed back.")
        
  def testFloorPointsOverall(self):
    """
    Tests calculating the floor points leaders in a round.
    """
    profile = self.users[0].get_profile()
    profile.add_points(10, datetime.datetime.today() - datetime.timedelta(minutes=1), "test")
    profile.save()

    self.assertEqual(self.dorms[0].floor_points_leaders()[0], profile.floor, 
        "The user's floor is not leading in the prize.")

    # Test that a user in a different floor but same dorm changes the leader for the original user.
    profile2 = self.users[2].get_profile()
    profile2.add_points(profile.points + 1, datetime.datetime.today() - datetime.timedelta(minutes=1), "test")
    profile2.save()

    self.assertEqual(self.dorms[0].floor_points_leaders()[0], profile2.floor, 
        "The user's floor should have changed.")

    # Test that a tie between two different floors is handled properly.
    profile.add_points(1, datetime.datetime.today(), "test")
    profile.save()
    
    self.assertEqual(profile.points, profile2.points, "The two profiles should have identical points.")
    self.assertEqual(self.dorms[0].floor_points_leaders()[0], profile.floor, 
        "The leader of the floor should have changed back.")

    # Test that adding points to a user in a different dorm does not change affect these standings.
    profile1 = self.users[1].get_profile()
    profile1.add_points(profile.points + 1, datetime.datetime.today() - datetime.timedelta(minutes=1), "test")
    profile1.save()

    self.assertEqual(self.dorms[0].floor_points_leaders()[0], profile.floor, 
        "The leader of the floor should not change.")
    self.assertEqual(self.dorms[1].floor_points_leaders()[0], profile1.floor, 
        "The leader in the second dorm should be profile1's floor.")
        
  def tearDown(self):
    settings.COMPETITION_ROUNDS = self.saved_rounds
    
class FloorLeadersTestCase(TestCase):
  def setUp(self):
    self.dorm = Dorm(name="Test Dorm")
    self.dorm.save()
    
    self.floors = [Floor(number=str(i), dorm=self.dorm) for i in range(0, 2)]
    map(lambda f: f.save(), self.floors)
    
    self.users = [User.objects.create_user("test%d" % i, "test@test.com") for i in range(0, 4)]
    
    # Assign users to floors.
    for index, user in enumerate(self.users):
      user.get_profile().floor = self.floors[index % 2]
      user.get_profile().save()
      
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
    
  def testFloorPointsInRound(self):
    """
    Tests calculating the floor points leaders in a round.
    """
    profile = self.users[0].get_profile()
    profile.add_points(10, datetime.datetime.today() - datetime.timedelta(minutes=1), "test")
    profile.save()
    
    self.assertEqual(Floor.floor_points_leaders(round_name=self.current_round)[0], profile.floor, 
        "The user's floor is not leading in the prize.")
        
    # Test that a user in a different floor but same dorm changes the leader for the original user.
    profile2 = self.users[2].get_profile()
    profile2.add_points(profile.points + 1, datetime.datetime.today() - datetime.timedelta(minutes=1), "test")
    profile2.save()
    
    self.assertEqual(Floor.floor_points_leaders(round_name=self.current_round)[0], profile2.floor, 
        "The user's floor should have changed.")
        
    # Test that adding points outside of the round does not affect the leaders.
    profile.add_points(10, datetime.datetime.today() - datetime.timedelta(days=2), "test")
    profile.save()
    
    self.assertEqual(Floor.floor_points_leaders(round_name=self.current_round)[0], profile2.floor, 
        "The leader of the floor should not change.")
        
    # Test that a tie is handled properly.
    profile.add_points(1, datetime.datetime.today(), "test")
    profile.save()
    
    self.assertEqual(Floor.floor_points_leaders(round_name=self.current_round)[0], profile.floor, 
        "The leader of the floor should have changed back.")
        
  def testIndividualPointsInRound(self):
    """
    Tests calculating the individual points leaders in a round.
    """
    profile = self.users[0].get_profile()
    profile.add_points(10, datetime.datetime.today() - datetime.timedelta(minutes=1), "test")
    profile.save()

    self.assertEqual(profile.floor.points_leaders(round_name=self.current_round)[0], profile, 
        "The user should be in the lead in his own floor.")

    # Test that a user in a different floor but same dorm does not change the leader for the original floor.
    profile1 = self.users[1].get_profile()
    profile1.add_points(15, datetime.datetime.today() - datetime.timedelta(minutes=1), "test")
    profile1.save()
    
    self.assertEqual(profile.floor.points_leaders(round_name=self.current_round)[0], profile, 
        "The leader for the user's floor should not have changed.")
    self.assertEqual(profile1.floor.points_leaders(round_name=self.current_round)[0], profile1, 
        "User 1 should be leading in their own floor.")
        
    # Test another user going ahead in the user's floor.
    profile2 = self.users[2].get_profile()
    profile2.add_points(15, datetime.datetime.today() - datetime.timedelta(minutes=1), "test")
    profile2.save()

    self.assertEqual(profile.floor.points_leaders(round_name=self.current_round)[0], profile2, 
        "User 2 should be in the lead in the user's floor.")
        
    # Test that adding points outside of the round does not affect the leaders.
    profile.add_points(10, datetime.datetime.today() - datetime.timedelta(days=2), "test")
    profile.save()

    self.assertEqual(profile.floor.points_leaders(round_name=self.current_round)[0], profile2, 
        "The leader of the floor should not change.")

    # Test that a tie is handled properly.
    profile.add_points(5, datetime.datetime.today(), "test")
    profile.save()

    self.assertEqual(profile.floor.points_leaders(round_name=self.current_round)[0], profile, 
        "The leader of the floor should have changed back.")
        
  def testFloorPointsOverall(self):
    """
    Tests calculating the floor points leaders in a round.
    """
    profile = self.users[0].get_profile()
    profile.add_points(10, datetime.datetime.today() - datetime.timedelta(minutes=1), "test")
    profile.save()

    self.assertEqual(profile.floor.points_leaders()[0], profile, 
        "The user should be in the lead in his own floor.")

    # Test that a user in a different floor but same dorm does not change the leader for the original floor.
    profile1 = self.users[1].get_profile()
    profile1.add_points(15, datetime.datetime.today() - datetime.timedelta(minutes=1), "test")
    profile1.save()

    self.assertEqual(profile.floor.points_leaders()[0], profile, 
        "The leader for the user's floor should not have changed.")
    self.assertEqual(profile1.floor.points_leaders()[0], profile1, 
        "User 1 should be leading in their own floor.")
        
    # Test another user going ahead in the user's floor.
    profile2 = self.users[2].get_profile()
    profile2.add_points(15, datetime.datetime.today() - datetime.timedelta(minutes=1), "test")
    profile2.save()

    self.assertEqual(profile.floor.points_leaders()[0], profile2, 
        "User 2 should be in the lead in the user's floor.")

    # Test that a tie is handled properly.
    profile.add_points(5, datetime.datetime.today(), "test")
    profile.save()

    self.assertEqual(profile.floor.points_leaders()[0], profile, 
        "The leader of the floor should have changed back.")
        
  def tearDown(self):
    settings.COMPETITION_ROUNDS = self.saved_rounds

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
    
    user.get_profile().add_points(user_points, datetime.datetime.today(), "test")
    user.get_profile().save()
    
    self.assertEqual(self.test_floor.points(), user_points, "Check that the number of points are equal for one user.")
    
    # Create another test user and check again.
    user = User(username="test_user1", password="test_password")
    user.save()
    user.get_profile().floor = self.test_floor
    user.get_profile().add_points(user_points, datetime.datetime.today(), "test")
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
    
    profile.add_points(10, datetime.datetime.today(), "test")
    profile.save()
    
    self.assertEqual(self.test_floor.current_round_points(), 10, "Check that the number of points are correct in this round.")
    
    profile.add_points(10, datetime.datetime.today() - datetime.timedelta(days=3), "test")
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
    
    user.get_profile().add_points(user_points, datetime.datetime.today(), "test")
    user.get_profile().save()

    self.assertEqual(self.test_floor.rank(), 1, "Check the floor is now ranked number 1.")

    # Create a test user on a different floor.
    test_floor2 = Floor(number="B", dorm=self.dorm)
    test_floor2.save()
    
    user2 = User(username="test_user1", password="test_password")
    user2.save()
    user2.get_profile().floor = test_floor2
    user2.get_profile().add_points(user_points + 1, datetime.datetime.today(), "test")
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
    
    user.get_profile().add_points(user_points, datetime.datetime.today(), "test")
    user.get_profile().save()
    self.assertEqual(self.test_floor.current_round_rank(), 1, "Check the floor is now ranked number 1.")
    
    test_floor2 = Floor(number="B", dorm=self.dorm)
    test_floor2.save()
    
    user2 = User(username="test_user1", password="test_password")
    user2.save()
    user2.get_profile().floor = test_floor2
    user2.get_profile().add_points(user_points + 1, datetime.datetime.today(), "test")
    user2.get_profile().save()
    
    self.assertEqual(self.test_floor.current_round_rank(), 2, "Check the floor is now ranked number 2.")
    
    user.get_profile().add_points(user_points, datetime.datetime.today() - datetime.timedelta(days=3), "test")
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
    user.get_profile().add_points(user_points, datetime.datetime.today() - datetime.timedelta(days=3), "test")
    user.get_profile().save()

    # Create a test user on a different floor.
    test_floor2 = Floor(number="B", dorm=self.dorm)
    test_floor2.save()

    user = User(username="test_user1", password="test_password")
    user.save()
    user.get_profile().floor = test_floor2
    user.get_profile().add_points(user_points, datetime.datetime.today(), "test")
    user.get_profile().save()

    self.assertEqual(self.test_floor.rank(), 2, "Check that the floor is ranked second.")