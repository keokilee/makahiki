from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from components.floors.models import Floor

class HelpFunctionalTestCase(TestCase):
  fixtures = ["base_floors.json"]
  
  def setUp(self):
    self.user = User.objects.create_user("user", "user@test.com", password="changeme")
    floor = Floor.objects.all()[0]
    profile = self.user.get_profile()
    profile.floor = floor
    profile.setup_complete = True
    profile.setup_profile = True
    profile.save()
    
    self.client.login(username="user", password="changeme")
    
  def testIndex(self):
    """Check that we can load the index page."""
    response = self.client.get(reverse("help_index"))
    self.failUnlessEqual(response.status_code, 200)
    
  def testPageHelp(self):
    """
    Test that help topics are available on pages that have them enabled.
    Also check that it can be disabled.
    """
    pages_with_help = ["activity_index", "energy_index", "news_index", "profile_index", "prizes_index"]
    profile = self.user.get_profile()
    
    for page in pages_with_help:
      # Try accessing the page with help enabled
      response = self.client.get(reverse(page))
      self.assertContains(response, "Help Topics", count=1,
          msg_prefix="%s should have help topics." % page)
          
      # Now try without help enabled.
      profile.enable_help = False
      profile.save()
      response = self.client.get(reverse(page))
      self.assertNotContains(response, "Help Topics",
          msg_prefix="Help topics should be disabled for %s." % page)
          
      # Enable help for next iteration.
      profile.enable_help = True
      profile.save()
