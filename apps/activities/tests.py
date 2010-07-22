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
    self.assertTrue(activity_member.award_date == user.get_profile().last_awarded)
    
  def testUnapproveRemovesPoints(self):
    """Test that unapproving a user removes their points."""
    user = User.objects.all()[0]
    points = user.get_profile().points
    last_awarded = user.get_profile().last_awarded
    
    activity = Activity.objects.all()[0]
    
    activity_member = ActivityMember(user=user, activity=activity)
    activity_member.approval_status = "approved"
    activity_member.save()
    
    activity_member.approval_status = "rejected"
    activity_member.save()
    new_points = user.get_profile().points
    
    self.assertTrue(points == new_points)
    self.assertTrue(last_awarded == user.get_profile().last_awarded is None)
    
  def testDeleteRemovesPoints(self):
    """Test that deleting an approved ActivityMember removes their points."""
    
    user = User.objects.all()[0]
    points = user.get_profile().points
    last_awarded = user.get_profile().last_awarded
    
    activity = Activity.objects.all()[0]
    
    activity_member = ActivityMember(user=user, activity=activity)
    activity_member.approval_status = "approved"
    activity_member.save()
    
    activity_member.delete()
    new_points = user.get_profile().points
    
    self.assertTrue(points == new_points)
    self.assertTrue(last_awarded == user.get_profile().last_awarded is None)
    
class CommitmentsTestCase(TestCase):
  fixtures = ["base_data.json", "user_data.json"]
  
  def testCompletionAddsPoints(self):
    """Tests that completing a task adds points."""
    user = User.objects.all()[0]
    points = user.get_profile().points
    last_awarded = user.get_profile().last_awarded
    
    commitment = Commitment.objects.all()[0]
    commitment_member = CommitmentMember(user=user, commitment=commitment, completion_date=datetime.datetime.today())
    
    commitment_member.save()
    
    # Check that this does not change the user's points.
    self.assertTrue(points == user.get_profile().points)
    self.assertTrue(last_awarded == user.get_profile().last_awarded)
    
    commitment_member.award_date = datetime.datetime.today()
    commitment_member.save()
    points += commitment_member.commitment.point_value
    self.assertTrue(points, user.get_profile().points)
    self.assertTrue(user.get_profile().last_awarded == commitment_member.award_date)
    
  def testDeleteRemovesPoints(self):
    """Test that deleting a commitment member after it is completed removes the user's points."""
    user = User.objects.all()[0]
    points = user.get_profile().points
    last_awarded = user.get_profile().last_awarded
    
    commitment = Commitment.objects.all()[0]
    commitment_member = CommitmentMember(user=user, commitment=commitment, completion_date=datetime.datetime.today())
    commitment_member.save()
    
    commitment_member.award_date = datetime.datetime.today()
    commitment_member.save()
    commitment_member.delete()
    self.assertTrue(last_awarded == user.get_profile().last_awarded is None)
    self.assertTrue(points == user.get_profile().points)