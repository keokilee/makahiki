import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from components.floors.models import Floor
from components.activities.models import Activity, ActivityMember, Commitment, CommitmentMember

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
    self.assertContains(response, reverse("activity_task", args=(activity.id,)))
    self.assertContains(response, "Pending")
    self.assertContains(response, "You have not been awarded anything yet!")
    self.assertNotContains(response, "You have nothing in progress or pending.")
    
    # Test that the profile page has a rejected activity
    member.approval_status = "rejected"
    member.save()
    response = self.client.get(reverse("profile_index"))
    self.assertContains(response, reverse("activity_task", args=(activity.id,)))
    self.assertContains(response, "Rejected")
    self.assertContains(response, "You have not been awarded anything yet!")
    self.assertNotContains(response, "You have nothing in progress or pending.")
    
    # Test that the profile page has a completed activity
    member.approval_status = "approved"
    member.save()
    response = self.client.get(reverse("profile_index"))
    self.assertContains(response, reverse("activity_task", args=(activity.id,)))
    self.assertNotContains(response, "You have not been awarded anything yet!")
    self.assertContains(response, "You have nothing in progress or pending.")
    
  def testCommitmentAchievement(self):
    """Check that the user's achievements are loaded."""
    commitment = Commitment(
        title="Test commitment",
        description="A commitment!",
        point_value=10,
    )
    commitment.save()

    # Test that profile page has a pending activity.
    member = CommitmentMember(user=self.user, commitment=commitment)
    member.save()
    response = self.client.get(reverse("profile_index"))
    self.assertContains(response, reverse("activity_task", args=(commitment.id,)))
    self.assertContains(response, "In Progress")
    self.assertContains(response, "You have not been awarded anything yet!")
    self.assertNotContains(response, "You have nothing in progress or pending.")

    # Test that the profile page has a rejected activity
    member.award_date = datetime.datetime.today()
    member.save()
    response = self.client.get(reverse("profile_index"))
    self.assertContains(response, reverse("activity_task", args=(commitment.id,)))
    self.assertNotContains(response, "You have not been awarded anything yet!")
    self.assertContains(response, "You have nothing in progress or pending.")
    