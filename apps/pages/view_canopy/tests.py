from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User


class CanopyFunctionalTestCase(TestCase):
  def testIndex(self):
    """Check that we can load the index."""
    user = User.objects.create_user("user", "user@test.com", password="changeme")
    profile = user.get_profile()
    profile.setup_complete = True
    profile.setup_profile = True
    profile.save()
    self.client.login(username="user", password="changeme")
    
    response = self.client.get(reverse("canopy_index"))
    self.failUnlessEqual(response.status_code, 200)