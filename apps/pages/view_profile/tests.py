import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from components.floors.models import Floor
from components.activities.models import Activity, ActivityMember, Commitment, CommitmentMember
from pages.view_profile.forms import ProfileForm

class ProfileFunctionalTestCase(TestCase):
  fixtures = ["base_floors.json"]
  
  def setUp(self):
    self.user = User.objects.create_user("user", "user@test.com", password="changeme")
    self.floor = Floor.objects.all()[0]
    profile = self.user.get_profile()
    profile.floor = self.floor
    profile.setup_complete = True
    profile.setup_profile = True
    profile.save()
    
    self.client.login(username="user", password="changeme")
    
  def testIndex(self):
    """Check that we can load the index page."""
    response = self.client.get(reverse("profile_index"))
    self.failUnlessEqual(response.status_code, 200)
    
  def testProfileUpdate(self):
    """Tests updating the user's profile."""
    # Construct a valid form
    user_form = {
        "display_name": "Test User",
        "about": "I rock",
        "contact_email": "user@test.com",
        "contact_text": "8088675309",
        "contact_carrier": "tmobile",
    }
    # Test posting a valid form.
    response = self.client.post(reverse("profile_index"), user_form, follow=True)
    self.assertContains(response, "Your changes have been saved", 
        msg_prefix="Successful form update should have a success message.")
    
    # Try getting the form again to see if info sticked.
    response = self.client.get(reverse("profile_index"))
    self.assertContains(response, "user@test.com", count=1, msg_prefix="Contact email should be saved.")
    self.assertContains(response, "808-867-5309", count=1, msg_prefix="Phone number should be saved.")
    self.assertContains(response, '<option value="tmobile" selected="selected">', 
        msg_prefix="Carrier should be saved.")
    
    # Try posting the form again.
    response = self.client.post(reverse("profile_index"), user_form, follow=True)
    self.assertContains(response, "Your changes have been saved", 
        msg_prefix="Second form update should have a success message.")
        
    # Test posting an invalid form.
    user_form.update({"display_name": ""})
    response = self.client.post(reverse("profile_index"), user_form, follow=True)
    self.assertContains(response, "This field is required", 
        msg_prefix="User should not have a valid display name.")
    
    user_form.update({"display_name": "Test User", "contact_email": "foo"})
    response = self.client.post(reverse("profile_index"), user_form, follow=True)
    self.assertContains(response, "Enter a valid e-mail address", 
        msg_prefix="User should not have a valid email address")
        
    user_form.update({"contact_email": "user@test.com", "contact_text": "foo"})
    response = self.client.post(reverse("profile_index"), user_form, follow=True)
    self.assertContains(response, "Phone numbers must be in XXX-XXX-XXXX format.", 
        msg_prefix="User should not have a valid contact number.")
    
  def testProfileWithDupName(self):
    user = User.objects.create_user("user2", "user2@test.com")
    profile = user.get_profile()
    profile.name = "Test U."
    profile.save()
    
    user_form = {
        "display_name": "Test U.",
        "about": "I rock",
        "stay_logged_in": True,
        "contact_email": "user@test.com",
        "contact_text": "8088675309",
        "contact_carrier": "tmobile",
    }
    # Test posting form with dup name.
    response = self.client.post(reverse("profile_index"), user_form, follow=True)
    self.assertContains(response, "please enter another name.", 
        msg_prefix="Duplicate name should raise an error.")
        
    user_form.update({"display_name": "  Test U.     "})
    # Test posting a form with a dup name with a lot of whitespace.
    response = self.client.post(reverse("profile_index"), user_form, follow=True)
    self.assertContains(response, "please enter another name.", 
        msg_prefix="Duplicate name with whitespace should raise an error.")
    
  def testActivityAchievement(self):
    """Check that the user's activity achievements are loaded."""
    activity = Activity(
        title="Test activity",
        description="Testing!",
        duration=10,
        point_value=10,
        pub_date=datetime.datetime.today(),
        expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
        confirm_type="text",
        type="activity",
    )
    activity.save()
    
    # Test that profile page has a pending activity.
    member = ActivityMember(user=self.user, activity=activity, approval_status="pending")
    member.save()
    response = self.client.get(reverse("profile_index"))
    self.assertContains(response, reverse("activity_task", args=(activity.type, activity.slug,)))
    self.assertContains(response, "Pending")
    self.assertContains(response, "Activity:")
    self.assertContains(response, "You have not been awarded anything yet!")
    self.assertNotContains(response, "You have nothing in progress or pending.")
    
    # Test that the profile page has a rejected activity
    member.approval_status = "rejected"
    member.save()
    response = self.client.get(reverse("profile_index"))
    self.assertContains(response, reverse("activity_task", args=(activity.type, activity.slug,)))
    self.assertContains(response, "Rejected")
    self.assertContains(response, "You have not been awarded anything yet!")
    self.assertNotContains(response, "You have nothing in progress or pending.")
    
    # Test that the profile page has a completed activity
    member.approval_status = "approved"
    member.save()
    response = self.client.get(reverse("profile_index"))
    self.assertContains(response, reverse("activity_task", args=(activity.type, activity.slug,)))
    self.assertNotContains(response, "You have not been awarded anything yet!")
    self.assertContains(response, "You have nothing in progress or pending.")
    self.assertContains(response, "Activity:")
    
    # Test adding an event to catch a bug.
    event = Activity(
        title="Test event",
        description="Testing!",
        duration=10,
        point_value=10,
        pub_date=datetime.datetime.today(),
        expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
        confirm_type="text",
        type="event",
    )
    event.save()
    
    member = ActivityMember(user=self.user, activity=event, approval_status="pending")
    member.save()
    response = self.client.get(reverse("profile_index"))
    self.assertContains(response, reverse("activity_task", args=(activity.type, activity.slug,)))
    self.assertContains(response, "Pending")
    self.assertContains(response, "Activity:")
    self.assertContains(response, "Event:")
    self.assertNotContains(response, "You have nothing in progress or pending.")
    
  def testCommitmentAchievement(self):
    """Check that the user's commitment achievements are loaded."""
    commitment = Commitment(
        title="Test commitment",
        description="A commitment!",
        point_value=10,
        type="commitment",
    )
    commitment.save()

    # Test that profile page has a pending activity.
    member = CommitmentMember(user=self.user, commitment=commitment)
    member.save()
    response = self.client.get(reverse("profile_index"))
    self.assertContains(response, reverse("activity_task", args=(commitment.type, commitment.slug,)))
    self.assertContains(response, "In Progress")
    self.assertContains(response, "Commitment:")
    self.assertContains(response, "Made commitment:")
    self.assertNotContains(response, "You have nothing in progress or pending.")

    # Test that the profile page has a rejected activity
    member.award_date = datetime.datetime.today()
    member.save()
    response = self.client.get(reverse("profile_index"))
    self.assertContains(response, reverse("activity_task", args=(commitment.type, commitment.slug,)))
    self.assertNotContains(response, "You have not been awarded anything yet!")
    self.assertContains(response, "You have nothing in progress or pending.")
    
  def testVariablePointAchievement(self):
    """Test that a variable point activity appears correctly in the my achievements list."""
    activity = Activity(
                title="Test activity",
                slug="test-activity",
                description="Variable points!",
                duration=10,
                point_range_start=5,
                point_range_end=20,
                pub_date=datetime.datetime.today(),
                expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
                confirm_type="text",
                type="activity",
    )
    activity.save()
    
    points = self.user.get_profile().points
    member = ActivityMember.objects.create(
        user=self.user,
        activity=activity,
        approval_status="approved",
        points_awarded=13,
    )
    member.save()
    
    self.assertEqual(self.user.get_profile().points, points + 13, 
        "Variable number of points should have been awarded.")
    
    # Kludge to change point value for the info bar.
    profile = self.user.get_profile()
    profile.add_points(3, datetime.datetime.today())
    profile.save()
    
    response = self.client.get(reverse("profile_index"))
    self.assertContains(response, reverse("activity_task", args=(activity.type, activity.slug,)))
    # Note, this test may break if something in the page has the value 13.  Try finding another suitable number.
    # print response.content
    self.assertContains(response, "13", count=1, msg_prefix="13 points should appear for the activity.")
        
  def testSocialBonusAchievement(self):
    """Check that the social bonus appears in the my achievements list."""
    # Create a second test user.
    user2 = User.objects.create_user("user2", "user2@test.com")
    event = Activity.objects.create(
        title="Test event",
        slug="test-event",
        description="Testing!",
        duration=10,
        point_value=10,
        social_bonus=10,
        pub_date=datetime.datetime.today(),
        expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
        confirm_type="code",
        type="event",
    )
    
    # Create membership for the two users.
    member = ActivityMember.objects.create(
        user=self.user,
        activity=event,
        approval_status="approved",
        user_comment="user2@test.com",
    )
    member2 = ActivityMember.objects.create(
        user=user2,
        activity=event,
        approval_status="approved",
        user_comment="user@test.com",
    )
    
    response = self.client.get(reverse("profile_index"))
    self.assertContains(response, reverse("activity_task", args=(event.type, event.slug,)))
    self.assertContains(response, "plus social bonus", count=1, msg_prefix="Achievements should contain a social bonus entry")
    