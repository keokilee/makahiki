from django.test import TestCase
from django.core.urlresolvers import reverse

class LandingFunctionalTestCase(TestCase):
  def testLanding(self):
    """Check that we can load the landing page."""
    response = self.client.get(reverse("landing"))
    self.failUnlessEqual(response.status_code, 200)