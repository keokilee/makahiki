from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings

from components.floors.models import Floor

class LandingFunctionalTestCase(TestCase):
  fixtures = ["base_floors.json"]
  
  def testLanding(self):
    """Check that we can load the landing page."""
    response = self.client.get(reverse("root_index"))
    self.failUnlessEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "landing/index.html")
    
  def testRootRedirect(self):
    """
    Check that if a settings variable is set, then going to the root url redirects to the appropriate page.
    """
    current_setting = None
    if hasattr(settings, "ROOT_REDIRECT_URL"):
      current_setting = settings.ROOT_REDIRECT_URL
      
    settings.ROOT_REDIRECT_URL = reverse('coming_soon')
    response = self.client.get(reverse("root_index"), follow=True)
    self.failUnlessEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "landing/coming_soon.html")
    
    settings.ROOT_REDIRECT_URL = reverse('about')
    response = self.client.get(reverse("root_index"), follow=True)
    self.failUnlessEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "landing/about.html")
    
    settings.ROOT_REDIRECT_URL = None
    response = self.client.get(reverse("root_index"), follow=True)
    self.failUnlessEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "landing/index.html")
    
    settings.ROOT_REDIRECT_URL = current_setting
    
  def testLoggedInRedirect(self):
    """Tests that if the user is logged in, we redirect to the home page."""
    user = User.objects.create_user("user", "user@test.com", password="changeme")
    floor = Floor.objects.all()[0]
    profile = user.get_profile()
    profile.floor = floor
    profile.setup_complete = True
    profile.setup_profile = True
    profile.save()
    
    self.client.login(username="user", password="changeme")
    
    response = self.client.get(reverse("root_index"))
    self.assertRedirects(response, reverse("home_index"),
        msg_prefix="Landing page should redirect to home page for logged in users.")
        
  def testMobileRedirect(self):
    """Tests that the mobile redirection and the cookie that forces the desktop version."""
    response = self.client.get(reverse("root_index"),
        HTTP_USER_AGENT="Mozilla/5.0 (iPod; U; CPU like Mac OS X; en) AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/3A100a"
    )
    self.failUnlessEqual(response.status_code, 302, "Mobile device should redirect.")
    
    self.client.cookies['mobile-desktop'] = True
    
    response = self.client.get(reverse("root_index"),
        HTTP_USER_AGENT="Mozilla/5.0 (iPod; U; CPU like Mac OS X; en) AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/3A100a"
    )
    self.failUnlessEqual(response.status_code, 200, "Mobile device should not redirect.")
    self.assertTemplateUsed(response, "landing/index.html")
    