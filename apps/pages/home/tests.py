import json

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
    
class SetupWizardFunctionalTestCase(TestCase):
  def setUp(self):
    self.user = User.objects.create_user("user", "user@test.com", password="changeme")
    self.client.post("/account/login/", {"username": "user", "password": "changeme"}, follow=True)
  
  def testDisplaySetupWizard(self):
    """Check that the setup wizard is shown for new users."""
    response = self.client.get(reverse("home_index"))
    self.failUnlessEqual(response.status_code, 200)
    self.assertContains(response, "Introduction: Step 1 of 7")
    
    # Check that the user is redirected to the setup wizard even if they visit another page.
    response = self.client.get(reverse("profile_index"))
    self.assertRedirects(response, reverse("home_index"))
  
  def testSetupTerms(self):
    """Check that we can access the terms page of the setup wizard."""
    response = self.client.get(reverse("setup_terms"), {}, 
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    self.assertTemplateUsed(response, "home/first-login/terms.html")
    try:
      response_dict = json.loads(response.content)
    except ValueError:
      self.fail("Response JSON could not be decoded.")
      
  def testSetupFacebook(self):
    """Check that we can access the facebook page of the setup wizard."""
    response = self.client.get(reverse("setup_facebook"), {}, 
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    self.assertTemplateUsed(response, "home/first-login/facebook.html")
    try:
      response_dict = json.loads(response.content)
    except ValueError:
      self.fail("Response JSON could not be decoded.")
      
    # TODO: Test post method (requires a FB profile attached to the user)
    
  def testSetupProfile(self):
    """Check that we can access the profile page of the setup wizard."""
    profile = self.user.get_profile()
    profile.name = "Test User"
    profile.save()
    response = self.client.get(reverse("setup_profile"), {}, 
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    self.assertTemplateUsed(response, "home/first-login/profile.html")
    self.assertContains(response, profile.name)
    self.assertNotContains(response, "facebook_photo")
    try:
      response_dict = json.loads(response.content)
    except ValueError:
      self.fail("Response JSON could not be decoded.")
      
    # TODO: Test setup with a FB profile.
    
  def testSetupProfileUpdate(self):
    """Check that we can update the profile of the user in the setup wizard."""
    profile = self.user.get_profile()
    points = profile.points
    response = self.client.post(reverse("setup_profile"), {
        "display_name": "Test User",
        "about": "I'm a test user.",
    })
    self.failUnlessEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "home/first-login/activity.html")
    
    user = User.objects.get(username="user")
    self.assertEqual(points + 5, user.get_profile().points, "Check that the user has been awarded points.")
    self.assertTrue(user.get_profile().setup_profile, "Check that the user has now set up their profile.")
    
    # Check that updating again does not award more points.
    response = self.client.post(reverse("setup_profile"), {
        "display_name": "Test User",
        "about": "I'm not a test user.",
    })
    user = User.objects.get(username="user")
    self.assertEqual(points + 5, user.get_profile().points, "Check that the user was not awarded any more points.")
      
  def testSetupActivity(self):
    """Check that we can access the activity page of the setup wizard."""
    response = self.client.get(reverse("setup_activity"), {}, 
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    self.assertTemplateUsed(response, "home/first-login/activity.html")
    try:
      response_dict = json.loads(response.content)
    except ValueError:
      self.fail("Response JSON could not be decoded.")
      
  def testSetupQuestion(self):
    """Check that we can access the question page of the setup wizard."""
    response = self.client.get(reverse("setup_question"), {}, 
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    self.assertTemplateUsed(response, "home/first-login/question.html")
    try:
      response_dict = json.loads(response.content)
    except ValueError:
      self.fail("Response JSON could not be decoded.")

  def testSetupComplete(self):
    """
    Check that we can access the complete page of the setup wizard.
    """
    # Test a normal GET request (answer was incorrect).
    response = self.client.get(reverse("setup_complete"), {}, 
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    self.assertTemplateUsed(response, "home/first-login/complete.html")
    try:
      response_dict = json.loads(response.content)
    except ValueError:
      self.fail("Response JSON could not be decoded.")
      
    user = User.objects.get(username="user")
    self.assertTrue(user.get_profile().setup_complete, "Check that the user has completed the profile setup.")
    
    # Test a normal POST request (answer was correct).
    profile = user.get_profile()
    points = profile.points
    profile.setup_complete = False
    profile.save()
    
    response = self.client.post(reverse("setup_complete"), {}, 
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    self.assertTemplateUsed(response, "home/first-login/complete.html")
    try:
      response_dict = json.loads(response.content)
    except ValueError:
      self.fail("Response JSON could not be decoded.")
      
    user = User.objects.get(username="user")
    self.assertTrue(user.get_profile().setup_complete, "Check that the user has completed the profile setup.")
    self.assertEqual(points + 15, user.get_profile().points, "Check that the user has been awarded points as well.")