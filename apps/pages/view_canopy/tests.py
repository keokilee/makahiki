import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from components.activities.models import Activity, ActivityMember
from components.canopy.models import Mission

class CanopyFunctionalTestCase(TestCase):
  def setUp(self):
    self.user = User.objects.create_user("user", "user@test.com", password="atest")
    profile = self.user.get_profile()
    profile.name = "Test U."
    profile.setup_complete = True
    profile.setup_profile = True
    profile.save()
    self.client.login(username="user", password="atest")
    
  def testUserAccess(self):
    """Check that superusers, staff, and canopy members can access the canopy."""
    # Test that regular user cannot access the canopy.
    response = self.client.get(reverse("canopy_index"))
    self.failUnlessEqual(response.status_code, 404)
    
    # Test that a superuser can access the canopy
    self.user.is_superuser = True
    self.user.save()
    response = self.client.get(reverse("canopy_index"))
    self.failUnlessEqual(response.status_code, 200)
    self.assertContains(response, 'alt="Photo of Test U."', count=1)
    
    # Test that staff can access the canopy
    self.user.is_superuser = False
    self.user.is_staff = True
    self.user.save()
    response = self.client.get(reverse("canopy_index"))
    self.failUnlessEqual(response.status_code, 200)
    self.assertContains(response, 'alt="Photo of Test U."', count=1)
    
    # Test that canopy members can access the canopy
    self.user.is_staff = False
    self.user.save()
    profile = self.user.get_profile()
    profile.canopy_member = True
    profile.save()
    response = self.client.get(reverse("canopy_index"))
    self.failUnlessEqual(response.status_code, 200)
    self.assertContains(response, 'alt="Photo of Test U."', count=1)
    
class MissionsFunctionalTestCase(TestCase):
  def setUp(self):
    self.user = User.objects.create_user("user", "user@test.com", password="atest")
    profile = self.user.get_profile()
    profile.name = "Test U."
    profile.setup_complete = True
    profile.setup_profile = True
    profile.canopy_member = True
    profile.save()
    self.client.login(username="user", password="atest")
    
    self.activity = Activity.objects.create(
        title="Test activity",
        slug="test-activity",
        description="Testing!",
        duration=10,
        point_value=10,
        pub_date=datetime.datetime.today(),
        expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
        confirm_type="text",
        type="activity",
    )
    
    self.mission = Mission.objects.create(
        name="Test mission",
        slug="test-mission",
        description="A test mission",
        is_group=False
    )
    self.mission.activities.add(self.activity)
    
  def testSoloMission(self):
    """
    Test that a user can view and complete a solo mission.
    """
    response = self.client.get(reverse("canopy_index"))
    self.assertContains(response, "Be the first to complete this mission!")
    self.assertContains(response, "Test mission")
    self.assertContains(response, reverse("activity_task", args=(self.activity.type, self.activity.slug)))
    
    activity_member = ActivityMember(
        user=self.user,
        activity=self.activity,
        approval_status="approved"
    )
    activity_member.save()
    
    response = self.client.get(reverse("canopy_index"))
    
    self.assertNotContains(response, "Be the first to complete this mission!")
    self.assertContains(response, 'alt="Photo of Test U."', count=2)
    
  def testGroupMission(self):
    """
    Test that a user can complete a group mission.
    """
    self.mission.is_group = True
    self.mission.save()
    
    response = self.client.get(reverse("canopy_index"))
    self.assertContains(response, "Be the first to complete this mission!")
    self.assertContains(response, "No users are currently participating in this mission.")
    self.assertNotContains(response, reverse("activity_task", args=(self.activity.type, self.activity.slug)))
    self.assertContains(response, "Test mission")
    
    response = self.client.post(reverse("canopy_mission_accept", args=(self.mission.slug,)), follow=True)
    self.assertNotContains(response, "No users are currently participating in this mission.")
    self.assertContains(response, "Be the first to complete this mission!")
    self.assertContains(response, "The following users are up for this mission:")
    self.assertContains(response, reverse("activity_task", args=(self.activity.type, self.activity.slug)))
    self.assertContains(response, 'alt="Photo of Test U."', count=2)
    
    activity_member = ActivityMember(
        user=self.user,
        activity=self.activity,
        approval_status="approved"
    )
    activity_member.save()
    
    response = self.client.get(reverse("canopy_index"))
    
    self.assertNotContains(response, "Be the first to complete this mission!")
    self.assertContains(response, "No users are currently participating in this mission.")
    self.assertContains(response, 'alt="Photo of Test U."', count=2)
    
  def testCancelGroupMission(self):
    """
    Test that the user can cancel their participation in the group mission.
    """
    self.mission.is_group = True
    self.mission.save()
    
    response = self.client.post(reverse("canopy_mission_accept", args=(self.mission.slug,)), follow=True)
    self.assertNotContains(response, "No users are currently participating in this mission.")
    self.assertContains(response, "Be the first to complete this mission!")
    self.assertContains(response, "The following users are up for this mission:")
    self.assertContains(response, 'alt="Photo of Test U."', count=2)
    
    response = self.client.post(reverse("canopy_mission_cancel", args=(self.mission.slug,)), follow=True)
    self.assertContains(response, "Be the first to complete this mission!")
    self.assertContains(response, "No users are currently participating in this mission.")
    self.assertContains(response, 'alt="Photo of Test U."', count=1)