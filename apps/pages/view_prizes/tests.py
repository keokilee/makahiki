from django.test import TestCase
from django.core.urlresolvers import reverse

class PrizesFunctionalTestCase(TestCase):
  def testIndex(self):
    """Check that we can load the index page."""
    self.client.login(username="user", password="changeme")
    
    response = self.client.get(reverse("prizes_index"))
    self.failUnlessEqual(response.status_code, 200)