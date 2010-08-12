import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from floors.models import Floor
from django.core.urlresolvers import reverse
    
class FloorsFunctionalTestCase(TestCase):
  fixtures = ["base_data.json", "user_data.json"]

  def testUnauthenticatedAccess(self):
    """Test that an unauthenticated user cannot access a floor or member list."""
    
    # Retrieve a floor that the user does not have access to.
    floor = Floor.objects.all()[0]
    response = self.client.get(reverse("floor_detail", args=(floor.dorm.slug, floor.number)))
    self.assertTemplateUsed(response, "restricted.html", msg_prefix="Test that user cannot access floor's detail page.")
    
    response = self.client.get(reverse("floor_members", args=(floor.dorm.slug, floor.number)))
    self.assertTemplateUsed(response, "restricted.html", msg_prefix="Test that user cannot access floor's member list.")
    
  def testAuthenticatedUserAccess(self):
    """Test that an authenticated user can only access their current floor and no others."""
    
    self.user = User.objects.get(username="user")
    self.client.post('/account/login/', {"username": self.user.username, "password": "changeme", "remember": False})
    
    # Verify user can access their own floor.
    profile = self.user.get_profile()
    response = self.client.get(reverse("floor_detail", args=(profile.floor.dorm.slug, profile.floor.number)))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "floors/floor_detail.html")
    
    response = self.client.get(reverse("floor_members", args=(profile.floor.dorm.slug, profile.floor.number)))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "floors/members.html")
    
    # Retrieve a floor that the user does not have access to.
    floor = Floor.objects.exclude(dorm=profile.floor.dorm, number=profile.floor.number)[0]
    response = self.client.get(reverse("floor_detail", args=(floor.dorm.slug, floor.number)))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "restricted.html", msg_prefix="Test that user cannot access another floor's detail page.")
    
    response = self.client.get(reverse("floor_members", args=(floor.dorm.slug, floor.number)))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "restricted.html", msg_prefix="Test that user cannot access another floor's member list.")
    
  def testAdminAccess(self):
    """Test that an admin can access any floor page."""
    
    # Log in as admin.
    self.client.post('/account/login/', {"username": "admin", "password": "changeme", "remember": False})
    
    floor = Floor.objects.all()[0]
    response = self.client.get(reverse("floor_detail", args=(floor.dorm.slug, floor.number)))
    self.assertTemplateUsed(response, "floors/floor_detail.html", msg_prefix="Test admin can access detail page.")
    self.assertEqual(response.status_code, 200)
    response = self.client.get(reverse("floor_members", args=(floor.dorm.slug, floor.number)))
    self.assertTemplateUsed(response, "floors/members.html", msg_prefix="Test admin can access member list.")
    self.assertEqual(response.status_code, 200)