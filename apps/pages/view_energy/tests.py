from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from components.floors.models import Floor
from components.energy_goals.models import FloorEnergyGoal

class EnergyFunctionalTestCase(TestCase):
  fixtures = ["base_floors.json"]
  
  def setUp(self):
    """Initialize a user and log them in."""
    self.user = User.objects.create_user("user", "user@test.com", password="changeme")
    self.floor = Floor.objects.all()[0]
    profile = self.user.get_profile()
    profile.floor = self.floor
    profile.setup_complete = True
    profile.setup_profile = True
    profile.save()
    
    self.client.login(username="user", password="changeme")
    
  def testIndex(self):
    """Check that we can load the index page."""
    response = self.client.get(reverse("energy_index"))
    self.failUnlessEqual(response.status_code, 200)
    
  def testEnergyScoreboard(self):
    response = self.client.get(reverse("energy_index"))
    goals = response.context["goals_scoreboard"]
    for goal in goals:
      self.assertEqual(goal["completions"], 0, "No floor should have completed a goal.")
      
    goal = FloorEnergyGoal.objects.create(
        floor=self.floor,
        goal_usage="1.0",
        actual_usage="2.0",
    )
    
    response = self.client.get(reverse("energy_index"))
    goals = response.context["goals_scoreboard"]
    for goal in goals:
      self.assertEqual(goal["completions"], 0, "No floor should have completed a goal.")
      
    goal = FloorEnergyGoal.objects.create(
        floor=self.floor,
        goal_usage="1.0",
        actual_usage="0.5",
    )

    response = self.client.get(reverse("energy_index"))
    goals = response.context["goals_scoreboard"]
    for floor in goals:
      if floor["floor__number"] == self.floor.number and floor["floor__dorm__name"] == self.floor.dorm.name:
        # print floor.floorenergygoal_set.all()
        self.assertEqual(floor["completions"], 1, 
            "User's floor should have completed 1 goal, but completed %d" % floor["completions"])
      else:
        self.assertEqual(floor["completions"], 0, "No floor should have completed a goal.")