from django.test import TestCase
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User

class HomeFunctionalTestCase(TestCase):
  def testIndex(self):
    """Check that we can load the index."""
    user = User.objects.create_user("user", "user@test.com", password="changeme")
    response = self.client.post("/account/login/", {"username": "user", "password": "changeme"}, follow=True)
    self.assertTemplateUsed(response, "home/index.html")
    
    response = self.client.get(reverse("home_index"))
    self.failUnlessEqual(response.status_code, 200)

