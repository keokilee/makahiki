import json
import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings

from components.activities.models import Activity, ActivityMember
from components.makahiki_profiles.models import Profile

class HomeFunctionalTestCase(TestCase):
  def testIndex(self):
    """Check that we can load the index."""
    user = User.objects.create_user("user", "user@test.com", password="changeme")
    self.client.login(username="user", password="changeme")
    
    response = self.client.get(reverse("home_index"))
    self.failUnlessEqual(response.status_code, 200)
    
class CompetitionMiddlewareTestCase(TestCase):
  def setUp(self):
    user = User.objects.create_user("user", "user@test.com", password="changeme")
    self.client.login(username="user", password="changeme")
    
    # Save settings that will be restored later.
    self.saved_start = settings.COMPETITION_START
    self.saved_end = settings.COMPETITION_END
    
    self.saved_access = settings.CAN_ACCESS_OUTSIDE_COMPETITION
    settings.CAN_ACCESS_OUTSIDE_COMPETITION = False
    
  def testBeforeCompetition(self):
    """
    Check that the user is redirected before the competition starts.
    """
    start = datetime.date.today() + datetime.timedelta(days=1)
    settings.COMPETITION_START = start.strftime("%Y-%m-%d")
    settings.COMPETITION_END = (start + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    
    response = self.client.get(reverse("home_index"), follow=True)
    self.failUnlessEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "home/restricted.html")
    self.assertContains(response, "The competition starts in")
    
  def testAfterCompetition(self):
    """
    Check that the user is redirected after the competition ends.
    """
    start = datetime.date.today() - datetime.timedelta(days=8)
    settings.COMPETITION_START = start.strftime("%Y-%m-%d")
    settings.COMPETITION_END = (start + datetime.timedelta(days=7)).strftime("%Y-%m-%d")

    response = self.client.get(reverse("home_index"), follow=True)
    self.failUnlessEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "home/restricted.html")
    self.assertContains(response, "The competition ended at midnight on")
    
  def tearDown(self):
    settings.COMPETITION_START = self.saved_start
    settings.COMPETITION_END = self.saved_end
    settings.CAN_ACCESS_OUTSIDE_COMPETITION = self.saved_access
  
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
    
  def testReferralStep(self):
    """
    Test that we can record referral emails from the setup page.
    """
    user2 = User.objects.create_user("user2", "user2@test.com")
    
    # Test we can get the referral page.
    response = self.client.get(reverse('setup_referral'), {},
               HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    self.failUnlessEqual(response.status_code, 200)
    try:
      response_dict = json.loads(response.content)
    except ValueError:
      self.fail("Response JSON could not be decoded.")
      
    # Test referring using their own email
    response = self.client.post(reverse('setup_referral'), {
        'referrer_email': self.user.email,
    }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    self.failUnlessEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "home/first-login/referral.html")
    self.assertEqual(len(response.context['form'].errors), 1, "Using their own email as referrer should raise an error.")

    # Test referring using the email of a user who is not in the system.
    response = self.client.post(reverse('setup_referral'), {
        'referrer_email': 'user@foo.com',
    }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    self.failUnlessEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "home/first-login/referral.html")
    self.assertEqual(len(response.context['form'].errors), 1, 'Using external email as referrer should raise an error.')
        
    # Test bad email.
    response = self.client.post(reverse('setup_referral'), {
        'referrer_email': 'foo',
    }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    self.failUnlessEqual(response.status_code, 200)
    self.assertEqual(len(response.context['form'].errors), 1, 'Using a bad email should insert an error.')
    self.assertTemplateUsed(response, "home/first-login/referral.html")
        
    # Test no referrer.
    response = self.client.post(reverse('setup_referral'), {
        'referrer_email': '',
    }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    self.failUnlessEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "home/first-login/profile.html")
    
    # Test successful referrer
    response = self.client.post(reverse('setup_referral'), {
        'referrer_email': user2.email,
    }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    self.failUnlessEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "home/first-login/profile.html")
    profile = Profile.objects.get(user=self.user)
    self.assertEqual(profile.referring_user, user2, 'User 1 should be referred by user 2.')
    
    # Test getting the referral page now has user2's email.
    response = self.client.get(reverse('setup_referral'), {},
               HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    self.failUnlessEqual(response.status_code, 200)
    self.assertContains(response, user2.email, msg_prefix="Going back to referral page should have second user's email.")
    
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
    }, follow=True)
    self.failUnlessEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "home/first-login/activity.html")
    
    user = User.objects.get(username="user")
    self.assertEqual(points + 5, user.get_profile().points, "Check that the user has been awarded points.")
    self.assertTrue(user.get_profile().setup_profile, "Check that the user has now set up their profile.")
    
    # Check that updating again does not award more points.
    response = self.client.post(reverse("setup_profile"), {
        "display_name": "Test User",
    }, follow=True)
    user = User.objects.get(username="user")
    self.assertEqual(points + 5, user.get_profile().points, "Check that the user was not awarded any more points.")
    self.failUnlessEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "home/first-login/activity.html")
    
  def testSetupProfileWithoutName(self):
    """Test that there is an error when the user does not supply a username."""
    profile = self.user.get_profile()
    response = self.client.post(reverse("setup_profile"), {
        "display_name": "",
    })
    self.failUnlessEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "home/first-login/profile.html")
    
  def testSetupProfileWithDupName(self):
    """Test that there is an error when the user uses a duplicate display name."""
    profile = self.user.get_profile()
    
    user2 = User.objects.create_user("user2", "user2@test.com")
    profile2 = user2.get_profile()
    profile2.name = "Test U."
    profile2.save()
    
    response = self.client.post(reverse("setup_profile"), {
        "display_name": "Test U.",
    }, follow=True)
    self.failUnlessEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "home/first-login/profile.html")
    self.assertContains(response, "please enter another name.", 
        msg_prefix="Duplicate name should raise an error.")
        
    response = self.client.post(reverse("setup_profile"), {
        "display_name": "   Test U.    ",
    }, follow=True)
    self.failUnlessEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "home/first-login/profile.html")
    self.assertContains(response, "please enter another name.", 
        msg_prefix="Duplicate name with whitespace should raise an error.")
    
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
      