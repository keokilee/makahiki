import json
import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings

from components.activities.models import Activity, ActivityMember

class HomeFunctionalTestCase(TestCase):
  def testIndex(self):
    """Check that we can load the index."""
    user = User.objects.create_user("user", "user@test.com", password="changeme")
    self.client.login(username="user", password="changeme")
    
    response = self.client.get(reverse("home_index"))
    self.failUnlessEqual(response.status_code, 200)
  
class SetupWizardFunctionalTestCase(TestCase):
  def setUp(self):
    self.user = User.objects.create_user("user", "user@test.com", password="changeme")
    self.client.login(username="user", password="changeme")
    
  def testMobileRedirect(self):
    """Check that a new user is taken to the mobile splash page."""
    # Make the request emulating a mobile browser.
    response = self.client.get(reverse("mobile_index"), 
        HTTP_USER_AGENT="Mozilla/5.0 (iPod; U; CPU like Mac OS X; en) AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/3A100a",
        follow=True)
    self.failUnlessEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "mobile/setup.html")
  
  def testDisplaySetupWizard(self):
    """Check that the setup wizard is shown for new users."""
    response = self.client.get(reverse("home_index"))
    self.failUnlessEqual(response.status_code, 200)
    self.assertContains(response, "Introduction: Step 1 of 6")
    
    # Check that the user is redirected to the setup wizard even if they visit another page.
    response = self.client.get(reverse("profile_index"))
    self.assertRedirects(response, reverse("home_index"))
  
  def testSetupTerms(self):
    """Check that we can access the terms page of the setup wizard."""
    response = self.client.get(reverse("setup_terms"), {}, 
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    self.assertTemplateUsed(response, "home/first-login/terms.html")
    self.assertContains(response, "/account/cas/logout?next=" + reverse("about"))
    try:
      response_dict = json.loads(response.content)
    except ValueError:
      self.fail("Response JSON could not be decoded.")
    
    
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
    }, follow=True)
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
    
  def testSetupProfileWithoutName(self):
    """Test that there is an error when the user does not supply a username."""
    profile = self.user.get_profile()
    points = profile.points
    response = self.client.post(reverse("setup_profile"), {
        "display_name": "",
        "about": "I'm a test user.",
    })
    self.failUnlessEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "home/first-login/profile.html")
      
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
    
    # Create the activity to link to.
    activity = Activity(
        title="Test activity",
        name=settings.SETUP_WIZARD_ACTIVITY_NAME,
        description="Testing!",
        duration=10,
        point_value=15,
        pub_date=datetime.datetime.today(),
        expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
        confirm_type="text",
        type="activity",
    )
    activity.save()
    
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
    member = ActivityMember.objects.get(user=user, activity=activity)
    self.assertEqual(member.approval_status, "approved", "Test that the user completed the linked activity.")
    
  def testMobileSetupComplete(self):
    """Check that the link at the end of the setup takes the user to the mobile page.."""
    # Make the request emulating a mobile browser.
    response = self.client.get(reverse("setup_complete"), 
        HTTP_USER_AGENT="Mozilla/5.0 (iPod; U; CPU like Mac OS X; en) AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/3A100a",
        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        follow=True,)
    self.failUnlessEqual(response.status_code, 200)
    self.assertContains(response, reverse("mobile_index"), count=1)
    
    # Test that the user can now access the mobile home page.
    response = self.client.get(reverse("mobile_index"), 
        HTTP_USER_AGENT="Mozilla/5.0 (iPod; U; CPU like Mac OS X; en) AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/3A100a",
        follow=True,)
    self.failUnlessEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "mobile/index.html")
      