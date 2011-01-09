import datetime

from django.conf import settings
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from components.activities.models import Activity, ActivityMember
from components.floors.models import Dorm, Floor
from components.makahiki_profiles.models import Profile, ScoreboardEntry
    
class ScoreboardEntryUnitTests(TestCase):
  def setUp(self):
    """Generate test user and activity. Set the competition settings to the current date for testing."""
    self.user = User(username="test_user", password="changeme")
    self.user.save()
    self.activity = Activity(
                title="Test activity",
                description="Testing!",
                duration=10,
                point_value=10,
                pub_date=datetime.datetime.today(),
                expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
                confirm_type="text",
    )
    self.activity.save()
    
    self.saved_rounds = settings.COMPETITION_ROUNDS
    self.current_round = "Round 1"
    start = datetime.date.today()
    end = start + datetime.timedelta(days=7)
    
    settings.COMPETITION_ROUNDS = {
      "Round 1" : {
        "start": start.strftime("%Y-%m-%d"),
        "end": end.strftime("%Y-%m-%d"),
      },
    }
    
  def testRoundsUpdate(self):
    """Test that the score for the round updates when an activity is approved."""
    entry, created = ScoreboardEntry.objects.get_or_create(
                        profile=self.user.get_profile(), 
                        round_name=self.current_round,
                      )
    round_points = entry.points
    round_submission_date = entry.last_awarded_submission
    
    activity_points = self.activity.point_value

    activity_member = ActivityMember(user=self.user, activity=self.activity)
    activity_member.approval_status = "approved"
    activity_member.save()
    
    # Verify that the points for the round has been updated.
    entry, created = ScoreboardEntry.objects.get_or_create(
                        profile=self.user.get_profile(), 
                        round_name=self.current_round,
                      )
                    
    self.assertEqual(round_points + activity_points, entry.points)
    self.assertNotEqual(round_submission_date, entry.last_awarded_submission)
    
  def testRoundDoesNotUpdate(self):
    """Test that the score for the round does not update for an activity submitted outside of the round."""
    entry, created = ScoreboardEntry.objects.get_or_create(
                        profile=self.user.get_profile(), 
                        round_name=self.current_round,
                      )
    round_points = entry.points
    round_submission_date = entry.last_awarded_submission

    activity_member = ActivityMember(user=self.user, activity=self.activity)
    activity_member.approval_status = "approved"
    activity_member.submission_date = datetime.datetime.today() - datetime.timedelta(days=1)
    activity_member.save()

    # Verify that the points for the round has not been updated.
    entry, created = ScoreboardEntry.objects.get_or_create(
                        profile=self.user.get_profile(), 
                        round_name=self.current_round,
                      )
                      
    self.assertEqual(round_points, entry.points)
    self.assertEqual(round_submission_date, entry.last_awarded_submission)
    
  def tearDown(self):
    """Restore the saved settings."""
    settings.COMPETITION_ROUNDS = self.saved_rounds
    
class ProfileUnitTests(TestCase):
  def testFloorRank(self):
    """Tests that the floor_rank method accurately computes the rank."""
    user = User(username="test_user", password="changeme")
    user.save()
    dorm = Dorm(name="Test dorm")
    dorm.save()
    floor = Floor(number="A", dorm=dorm)
    floor.save()
    
    profile = user.get_profile()
    profile.floor = floor
    top_user  = Profile.objects.all().order_by("-points")[0]
    profile.points = top_user.points + 1
    profile.save()
    
    self.assertEqual(profile.floor_rank(), 1, "Check that the user is number 1.")
    
    user2 = User(username="test_user2", password="changeme")
    user2.save()
    
    profile2 = user2.get_profile()
    profile2.points = profile.points + 1
    profile2.save()
    
    self.assertEqual(profile.floor_rank(), 1, 
                  "Check that the user is still number 1 if the new profile is not on the same floor.")
                  
    profile2.floor = floor
    profile2.save()
    
    self.assertEqual(profile.floor_rank(), 2, "Check that the user is now rank 2.")
    
  def testOverallRank(self):
    """Tests that the rank method accurately computes the rank."""
    user = User(username="test_user", password="changeme")
    user.save()
    
    profile = user.get_profile()
    top_user  = Profile.objects.all().order_by("-points")[0]
    profile.points = top_user.points + 1
    profile.save()
    
    self.assertEqual(profile.overall_rank(), 1, "Check that the user is number 1.")
    
    user2 = User(username="test_user2", password="changeme")
    user2.save()
    
    profile2 = user2.get_profile()
    profile2.points = profile.points + 1
    profile2.save()
    
    self.assertEqual(profile.overall_rank(), 2, "Check that the user is now rank 2.")
    
    
  def testAwardRollback(self):
    """Tests that the last_awarded_submission field rolls back to a previous task."""
    user = User(username="test_user", password="changeme")
    user.save()
    
    activity1 = Activity(
                title="Test activity",
                description="Testing!",
                duration=10,
                point_value=10,
                pub_date=datetime.datetime.today(),
                expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
                confirm_type="text",
    )
    activity1.save()
    
    activity2 = Activity(
                title="Test activity 2",
                description="Testing!",
                duration=10,
                point_value=15,
                pub_date=datetime.datetime.today(),
                expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
                confirm_type="text",
    )
    activity2.save()
    activities = [activity1, activity2]
    
    # Submit the first activity.  This is what we're going to rollback to.
    activity_member = ActivityMember(user=user, activity=activities[0])
    activity_member.approval_status = "approved"
    activity_member.submission_date = datetime.datetime.today() - datetime.timedelta(days=1)
    activity_member.save()
    
    points = user.get_profile().points
    submit_date = user.get_profile().last_awarded_submission
    
    # Submit second activity.
    activity_member = ActivityMember(user=user, activity=activities[1])
    activity_member.approval_status = "approved"
    activity_member.submission_date = datetime.datetime.today()
    activity_member.save()
    
    activity_member.approval_status = "rejected"
    activity_member.save()
    
    # Verify that we rolled back to the previous activity.
    self.assertEqual(points, user.get_profile().points)
    self.assertTrue(abs(submit_date - user.get_profile().last_awarded_submission) < datetime.timedelta(minutes=1))
    