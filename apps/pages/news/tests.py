from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

class NewsFunctionalTestCase(TestCase):
  # fixtures = ["base_data.json", "user_data.json"]
  
  def testIndex(self):
    """Check that we can load the index page."""
    response = self.client.post("/account/login/", {"username": "user", "password": "changeme"})
    self.failUnlessEqual(response.status_code, 200)
    
    response = self.client.get(reverse("news_index"))
    self.failUnlessEqual(response.status_code, 200)