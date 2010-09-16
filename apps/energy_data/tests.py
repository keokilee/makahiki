import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse

from floors.models import Floor
from goals.models import EnergyGoal, FloorEnergyGoal

class EnergyDataFunctionalTestCase(TestCase):
  fixtures = ["base_data.json", "user_data.json"]

  def setUp(self):
    """Create a test goal and log in the user."""
    start = datetime.date.today() - datetime.timedelta(days=4)
    voting_end = start + datetime.timedelta(days=3)
    end = start + datetime.timedelta(days=7)
    self.goal = EnergyGoal(
          start_date=start,
          voting_end_date=voting_end,
          end_date=end,
    )
    self.goal.save()
    
  def testEnergyDataContainsGoals(self):
    """Test to check that the goal is available in the energy data page."""
    floor = Floor.objects.all()[0]
    
    # Check that there is no goal in the default view.
    url = reverse('energy_data')
    url += "?floor=%d" % floor.pk
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200, "Test that there is no error in retrieving the energy data page.")
    self.assertEqual(response.context["floor"], floor, "Check that the floor is added in the context.")
    self.assertTrue(response.context["goal"] is None, "Check that the goal is not available.")
    
    # Create the energy goal
    floor_goal = FloorEnergyGoal(floor=floor, goal=self.goal, percent_reduction=10)
    floor_goal.save()
    
    # Check that the goal is now in the response.
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200, "Test that there is no error in retrieving the energy data page.")
    self.assertEqual(response.context["goal"], floor_goal, "Check that the goal is available.")
    