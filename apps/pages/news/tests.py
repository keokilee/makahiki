from django.test import TestCase
from django.core.urlresolvers import reverse

class NewsFunctionalTestCase(TestCase):
  fixtures = ["base_data.json", "user_data.json"]
  
  def testIndex(self):
    """Check that we can load the index page."""
    self.client.login(username="user", password="changeme")
    
    response = self.client.get(reverse("news_index"))
    self.failUnlessEqual(response.status_code, 200)