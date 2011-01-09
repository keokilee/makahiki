from django.test import TestCase
from django.contrib.auth.models import User

from components.floors.models import Dorm, Floor

class FloorsUnitTestCase(TestCase):
  def testOverallPoints(self):
    """Check that retrieving the points for the floor is correct."""
    dorm = Dorm(name="Test dorm")
    dorm.save()
    test_floor = Floor(number="A", dorm=dorm)
    test_floor.save()
    
    # Create a test user.
    user = User(username="test_user", password="test_password")
    user.save()
    user_points = 10
    user.get_profile().floor = test_floor
    user.get_profile().points = user_points
    user.get_profile().save()
    
    self.assertEqual(test_floor.points(), user_points, "Check that the number of points are equal for one user.")
    
    # Create another test user and check again.
    user = User(username="test_user1", password="test_password")
    user.save()
    user.get_profile().floor = test_floor
    user.get_profile().points = user_points
    user.get_profile().save()
    
    self.assertEqual(test_floor.points(), 2*user_points, "Check that the number of points are equal for two users.")
    
  def testOverallPoints(self):
    """Check that retrieving the points for the floor is correct."""
    dorm = Dorm(name="Test dorm")
    dorm.save()
    test_floor = Floor(number="A", dorm=dorm)
    test_floor.save()

    # Create a test user.
    user = User(username="test_user", password="test_password")
    user.save()
    user_points = 10
    user.get_profile().floor = test_floor
    user.get_profile().points = user_points
    user.get_profile().save()

    self.assertEqual(test_floor.rank(), 1, "Check the floor is now ranked number 1.")

    # Create a test user on a different floor.
    test_floor2 = Floor(number="B", dorm=dorm)
    test_floor2.save()
    
    user = User(username="test_user1", password="test_password")
    user.save()
    user.get_profile().floor = test_floor2
    user.get_profile().points = user_points + 1
    user.get_profile().save()

    self.assertEqual(test_floor.rank(), 2, "Check that the floor is now ranked number 2.")