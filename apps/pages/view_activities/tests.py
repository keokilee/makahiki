from django.test import TestCase
from django.core.urlresolvers import reverse

class ActivitiesFunctionalTestCase(TestCase):
  def testIndex(self):
    """Check that we can load the index page."""
    self.client.login(username="user", password="changeme")
    
    response = self.client.get(reverse("activities_index"))
    self.failUnlessEqual(response.status_code, 200)