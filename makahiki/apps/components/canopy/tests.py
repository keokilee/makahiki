import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from components.canopy.models import Mission, MissionMember
from components.activities.models import Activity, ActivityMember
from components.makahiki_profiles.models import Profile

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
   
  def testGroupMissionKarma(self):
    """
    Test that karma for a group activity is handled properly.
    """
    user = User.objects.create_user("user", "user@test.com")
    user1 = User.objects.create_user('user2', 'user2@test.com')
    user2 = User.objects.create_user('user3', 'user3@test.com')

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
        is_group=True,
        is_canopy=True,
    )

    mission = Mission.objects.create(
        name="Test mission",
        slug="test-mission",
        description="A test mission",
        is_group=True
    )
    mission.activities.add(activity)

    # If group user is participating in this mission, ensure karma points are awarded to both users.
    MissionMember.objects.create(user=user, mission=mission)
    MissionMember.objects.create(user=user1, mission=mission)
    
    member = ActivityMember.objects.create(
        user=user, 
        activity=activity,
        approval_status='pending', 
        social_email=user1.email
    )
    member1 = ActivityMember.objects.create(
        user=user1, 
        activity=activity, 
        approval_status='approved', 
        social_email=user.email, 
        social_email2=user2.email
    )

    profile = Profile.objects.get(user=user)
    profile1 = Profile.objects.get(user=user1)
    profile2 = Profile.objects.get(user=user2)
    self.assertEqual(profile1.canopy_karma, 10, 'Group member should be awarded 10 karma.')
    self.assertTrue(MissionMember.objects.get(user=user1, mission=mission).completed, "Mission should now be completed.")
    self.assertEqual(profile.canopy_karma, 10, 'Group member should be awarded 10 karma.')
    self.assertTrue(MissionMember.objects.get(user=user, mission=mission).completed, "Mission should now be completed.")
    self.assertEqual(profile2.canopy_karma, 0, 'Group member not participating in the mission should be awarded 0 karma.')
    
    # If group user is not participating in this mission, ensure they get karma points when they do participate.
    MissionMember.objects.create(user=user2, mission=mission)
    
    profile2 = Profile.objects.get(user=user2)
    self.assertEqual(profile2.canopy_karma, 10, 'New group member should now be awarded 10 karma.')
    self.assertTrue(MissionMember.objects.get(user=user2, mission=mission).completed, "Mission should now be completed.")
    
  def testGroupMissionVariableKarma(self):
    """
    Test that karma for a group activity with variable karma points works properly.
    """
    user = User.objects.create_user("user", "user@test.com")
    user1 = User.objects.create_user('user2', 'user2@test.com')

    activity = Activity.objects.create(
        title="Test activity",
        slug="test-activity",
        description="Testing!",
        duration=10,
        point_range_start=10,
        point_range_end=50,
        pub_date=datetime.datetime.today(),
        expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
        confirm_type="text",
        type="activity",
        is_group=True,
        is_canopy=True,
    )

    mission = Mission.objects.create(
        name="Test mission",
        slug="test-mission",
        description="A test mission",
        is_group=True
    )
    mission.activities.add(activity)
    
    MissionMember.objects.create(user=user, mission=mission)
    MissionMember.objects.create(user=user1, mission=mission)
    
    member = ActivityMember.objects.create(
        user=user, 
        activity=activity,
        approval_status='pending', 
        social_email=user1.email
    )
    member1 = ActivityMember.objects.create(
        user=user1, 
        activity=activity, 
        approval_status='approved', 
        social_email=user.email, 
        points_awarded=30,
    )
    
    profile = Profile.objects.get(user=user)
    profile1 = Profile.objects.get(user=user1)
    self.assertEqual(profile1.canopy_karma, 30, 'Group member should be awarded 30 karma.')
    self.assertEqual(profile.canopy_karma, 30, 'Group member should be awarded 30 karma.')
    
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
      