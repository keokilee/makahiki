from django.test import TestCase
from django.core.urlresolvers import reverse

class HomeFunctionalTestCase(TestCase):
  def testIndex(self):
    """Check that we can load the index."""
    response = self.client.get(reverse("home_index"))
    self.failUnlessEqual(response.status_code, 200)

