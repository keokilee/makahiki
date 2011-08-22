import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from components.makahiki_profiles.models import PointsTransaction
  
class PointsLogTest(TestCase):
  def setUp(self):
    self.user = User.objects.create_user("test", "test@test.com")
  
  def testAddPoints(self):
    """
    Test that adding points creates a new entry in the points log.
    """
    log_count = PointsTransaction.objects.count()
    profile = self.user.get_profile()
    profile.add_points(10, datetime.datetime.today(), "Winner", None)
    profile.save()
    
    self.assertEqual(PointsTransaction.objects.count(), log_count + 1, "A new log should have been created.")
    log = profile.user.pointstransaction_set.all()[0]
    self.assertEqual(log.points, 10, "Points should have been awarded.")
    self.assertEqual(log.message, "Winner", "Message should have been added.")
    self.assertEqual(profile.last_awarded_submission, log.submission_date, "Submission dates should be the same.")
    
  def testRemovePoints(self):
    """
    Test that removing points adds a negative points entry in the log.
    """
    log_count = PointsTransaction.objects.count()
    profile = self.user.get_profile()
    profile.add_points(10, datetime.datetime.today(), "Winner")
    profile.save()
    
    profile.remove_points(5, datetime.datetime.today(), "Syke!")
    
    self.assertEqual(PointsTransaction.objects.count(), log_count + 2, "Logs should have been created.")
    log = profile.user.pointstransaction_set.all()[1]
    self.assertEqual(log.points, -5, "Points should have been awarded.")
    self.assertEqual(log.message, "Syke!", "Message should have been added.")