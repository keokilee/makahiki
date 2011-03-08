from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from components.floors.models import Floor

class LandingFunctionalTestCase(TestCase):
  fixtures = ["base_floors.json"]
  
  def testLanding(self):
    """Check that we can load the landing page."""
    response = self.client.get(reverse("landing"))
    self.failUnlessEqual(response.status_code, 200)
    
  def testLoggedInRedirect(self):
    """Tests that if the user is logged in, we redirect to the home page."""
    user = User.objects.create_user("user", "user@test.com", password="changeme")
    floor = Floor.objects.all()[0]
    profile = user.get_profile()
    profile.floor = floor
    profile.setup_complete = True
    profile.setup_profile = True
    profile.save()
    
    self.client.login(username="user", password="changeme")
    
    response = self.client.get(reverse("landing"))
    self.assertRedirects(response, reverse("home_index"),
        msg_prefix="Landing page should redirect to home page for logged in users.")