from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

class ProfileFunctionalTestCase(TestCase):
  def testIndex(self):
    """Check that we can load the index page."""
    user = User(username="user", password="changeme")
    user.save()
    
    self.client.login(username=user.username, password="changeme")
    
    response = self.client.get(reverse("profile_index"))
    self.failUnlessEqual(response.status_code, 200)