import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from components.canopy.models import Mission, MissionMember
from components.activities.models import Activity, ActivityMember

class MissionTest(TestCase):
  def testGroupMissionCompletion(self):
    """
    Test that a group mission is completed when its related activity is completed.
    """
    user = User.objects.create_user("user", "user@test.com")
    
    activity = Activity.objects.create(
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
    
    mission = Mission.objects.create(
        name="Test mission",
        slug="test-mission",
        description="A test mission",
        is_group=True
    )
    mission.activities.add(activity)
    
    mission_member = MissionMember.objects.create(
        user=user,
        mission=mission,
    )
    
    activity_member = ActivityMember(
        user=user,
        activity=activity,
        approval_status="pending"
    )
    activity_member.save()
    
    self.assertFalse(mission_member.completed, "User should not have completed this mission.")
    
    activity_member.approval_status = "approved"
    activity_member.save()
    mission_member = MissionMember.objects.get(user=user, mission=mission)
    self.assertTrue(mission_member.completed, "User should have completed this mission.")
      
  def testSoloMissionCompletion(self):
    """
    Test that a solo mission is completed when its related activity is completed.
    """
    user = User.objects.create_user("user", "user@test.com")
    
    activity = Activity.objects.create(
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
    
    mission = Mission.objects.create(
        name="Test mission",
        slug="test-mission",
        description="A test mission",
        is_group=False
    )
    mission.activities.add(activity)
    
    activity_member = ActivityMember(
        user=user,
        activity=activity,
        approval_status="pending"
    )
    activity_member.save()
    
    try:
      mission_member = MissionMember.objects.get(user=user, mission=mission, completed=True)
      self.fail("User should not have completed this mission.")
    except MissionMember.DoesNotExist:
      pass
    
    activity_member.approval_status = "approved"
    activity_member.save()
    
    try:
      mission_member = MissionMember.objects.get(user=user, mission=mission, completed=True)
    except MissionMember.DoesNotExist:
      self.fail("User should have completed this mission.")