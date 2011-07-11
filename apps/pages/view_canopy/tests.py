from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

class CanopyFunctionalTestCase(TestCase):
  def testUserAccess(self):
    """Check that superusers, staff, and canopy members can access the canopy."""
    user = User.objects.create_user("user", "user@test.com", password="atest")
    profile = user.get_profile()
    profile.name = "Test U."
    profile.setup_complete = True
    profile.setup_profile = True
    profile.save()
    self.client.login(username="user", password="atest")
    
    # Test that regular user cannot access the canopy.
    response = self.client.get(reverse("canopy_index"))
    self.failUnlessEqual(response.status_code, 404)
    
    # Test that a superuser can access the canopy
    user.is_superuser = True
    user.save()
    response = self.client.get(reverse("canopy_index"))
    self.failUnlessEqual(response.status_code, 200)
    self.assertContains(response, 'alt="Photo of Test U."', count=1)
    
    # Test that staff can access the canopy
    user.is_superuser = False
    user.is_staff = True
    user.save()
    response = self.client.get(reverse("canopy_index"))
    self.failUnlessEqual(response.status_code, 200)
    self.assertContains(response, 'alt="Photo of Test U."', count=1)
    
    # Test that canopy members can access the canopy
    user.is_staff = False
    user.save()
    profile = user.get_profile()
    profile.canopy_member = True
    profile.save()
    response = self.client.get(reverse("canopy_index"))
    self.failUnlessEqual(response.status_code, 200)
    self.assertContains(response, 'alt="Photo of Test U."', count=1)
    