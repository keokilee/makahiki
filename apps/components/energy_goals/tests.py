import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from components.floors.models import Dorm, Floor
from components.energy_goals.models import FloorEnergyGoal
from components.makahiki_profiles.models import Profile

class FloorEnergyGoalTest(TestCase):
  def setUp(self):
    dorm = Dorm.objects.create(name="Test Dorm")
    dorm.save()
    self.floor = Floor.objects.create(
        dorm=dorm,
        number="A"
    )
    
    self.user = User.objects.create_user("user", "user@test.com")
    profile = self.user.get_profile()
    profile.floor = self.floor
    profile.save()
    
  def testFloorEnergyGoal(self):
    profile = self.user.get_profile()
    points = profile.points
    
    goal = FloorEnergyGoal(
        floor=self.floor, 
        goal_usage=str(1.0), 
        actual_usage=str(0.5),
    )
    goal.save()
    profile = Profile.objects.get(user__username="user")
    self.assertEqual(profile.points, points, 
        "User that did not complete the setup process should not be awarded points.")
    
    profile.setup_complete = True
    profile.save()
    
    goal.actual_usage = "1.5"
    goal.save()
    profile = Profile.objects.get(user__username="user")
    self.assertEqual(profile.points, points, 
        "Floor that failed the goal should not be awarded any points.")
        
    goal.actual_usage = "0.5"
    goal.save()
    profile = Profile.objects.get(user__username="user")
    self.assertEqual(profile.points, points + FloorEnergyGoal.GOAL_POINTS,
        "User that setup their profile should be awarded points.")
    
    
    
