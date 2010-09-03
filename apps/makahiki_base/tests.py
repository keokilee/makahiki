import simplejson as json

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from makahiki_base.models import Article
from makahiki_base import get_round_info

class IndexFunctionalTestCase(TestCase):
  fixtures = ["base_data.json", "user_data.json"]
  
  def testHomepageRedirect(self):
    """Tests that a logged in user goes to their profile page."""
    
    response = self.client.get(reverse("index"))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "homepage.html", 
          "Check that the home page template is used for non-authenticated users.")
    
    user = User.objects.get(username="user")
    self.client.post('/account/login/', {"username": user.username, "password": "changeme", "remember": False})
    response = self.client.get(reverse("index"), follow=True)
    self.assertTemplateUsed(response, "makahiki_profiles/profile.html", "Check that the user is taken to their profile.")
    response = self.client.get(reverse("home"))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "homepage.html", 
          "Check that the home page is still accessible in the tab.")
          
  def testJsonConfiguration(self):
    """Tests that JSON configuration is stored within multiple pages for widgets."""
    
    round_json = json.dumps(get_round_info())
    response = self.client.get(reverse("index"))
    self.assertContains(response, round_json)
    
    user = User.objects.get(username="user")
    self.client.post('/account/login/', {"username": user.username, "password": "changeme", "remember": False})
    response = self.client.get(reverse("profile_detail", args=(user.pk,)))
    self.assertContains(response, round_json)
    