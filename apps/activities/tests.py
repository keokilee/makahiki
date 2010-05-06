import unittest

from django.contrib.auth.models import User
from kukui_cup_profile.models import Profile
from activities.models import Activity, ActivityMember

class ActivitiesTestCase(unittest.TestCase):
  def testApproveAddsPoints(self):
    """Test for verifying that approving a user awards them points."""
    user = User.objects.all()[0]
    points = user.get_profile().points
    
    activity = Activity.objects.all()[0]
    activity_points = activity.point_value
    
    activity_member = ActivityMember(user=user, activity=activity)
    activity_member.approval_status = "approved"
    activity_member.save()
    
    new_points = user.get_profile().points
    self.assertTrue(new_points - points == activity_points)
    self.assertTrue(activity_member.awarded)
    
  def testUnapproveRemovesPoints(self):
    """Test that unapproving a user removes their points."""
    user = User.objects.all()[0]
    points = user.get_profile().points
    
    activity = Activity.objects.all()[0]
    
    activity_member = ActivityMember(user=user, activity=activity)
    activity_member.approval_status = "approved"
    activity_member.save()
    
    activity_member.approval_status = "rejected"
    activity_member.save()
    new_points = user.get_profile().points
    
    self.assertTrue(points == new_points)
    self.assertFalse(activity_member.awarded)
    
  def testDeleteRemovesPoints(self):
    """Test that deleting an approved ActivityMember removes their points."""
    
    user = User.objects.all()[0]
    points = user.get_profile().points
    
    activity = Activity.objects.all()[0]
    
    activity_member = ActivityMember(user=user, activity=activity)
    activity_member.approval_status = "approved"
    activity_member.save()
    
    activity_member.delete()
    new_points = user.get_profile().points
    
    self.assertTrue(points == new_points)
