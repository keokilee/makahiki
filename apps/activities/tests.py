import datetime

from django.test import TestCase

from django.contrib.auth.models import User
from makahiki_profiles.models import Profile
from activities.models import Activity, ActivityMember, Commitment, CommitmentMember

class ActivitiesTestCase(TestCase):
  fixtures = ["base_data.json", "user_data.json"]
  
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
    
class CommitmentsTestCase(TestCase):
  fixtures = ["base_data.json", "user_data.json"]
  
  def testCompletionAddsPoints(self):
    """Tests that completing a task adds points."""
    user = User.objects.all()[0]
    points = user.get_profile().points
    
    commitment = Commitment.objects.all()[0]
    commitment_member = CommitmentMember(user=user, commitment=commitment, completion_date=datetime.datetime.today())
    
    commitment_member.save()
    self.assertTrue(points == user.get_profile().points)
    
    commitment_member.completed = datetime.datetime.today()
    commitment_member.save()
    points += commitment_member.commitment.point_value
    self.assertTrue(points, user.get_profile().points)
