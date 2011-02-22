from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from components.floors.models import Floor

class EnergyFunctionalTestCase(TestCase):
  fixtures = ["base_floors.json", "test_energy_goals.json"]
  
  def testIndex(self):
    """Check that we can load the index page."""
    user = User.objects.create_user("user", "user@test.com", password="changeme")
    floor = Floor.objects.all()[0]
    profile = user.get_profile()
    profile.floor = floor
    profile.setup_complete = True
    profile.setup_profile = True
    profile.save()
    
    self.client.login(username="user", password="changeme")
    
    response = self.client.get(reverse("energy_index"))
    self.failUnlessEqual(response.status_code, 200)