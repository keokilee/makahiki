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
    
  def testUserOverallRoundRankWithPoints(self):
    """Tests that the overall rank calculation for a user in a round is correct based on points."""
    profile = self.user.get_profile()
    top_entry  = ScoreboardEntry.objects.filter(round_name=self.current_round).order_by("-points")[0]
    entry, created = ScoreboardEntry.objects.get_or_create(
                        profile=self.user.get_profile(), 
                        round_name=self.current_round,
                      )
    entry.points = top_entry.points + 1
    entry.last_awarded_submission = datetime.datetime.today()
    entry.save()
    
    self.assertEqual(ScoreboardEntry.user_round_overall_rank(self.user, self.current_round), 1, 
                    "Check user is ranked #1 for the current round.")
    
    user2 = User(username="test_user2", password="changeme")
    user2.save()

    profile2 = user2.get_profile()
    entry2, created = ScoreboardEntry.objects.get_or_create(
                        profile=profile2, 
                        round_name=self.current_round,
                      )
    entry2.points = entry.points + 1
    entry2.last_awarded_submission = entry.last_awarded_submission
    entry2.save()
    
    self.assertEqual(ScoreboardEntry.user_round_overall_rank(self.user, self.current_round), 2, 
                    "Check user is now second.")
                    
  def testUserOverallRoundRankWithSubmissionDate(self):
    """Tests that the overall rank calculation for a user in a round is correct based on submission date."""
    profile = self.user.get_profile()
    top_entry  = ScoreboardEntry.objects.filter(round_name=self.current_round).order_by("-points")[0]
    entry, created = ScoreboardEntry.objects.get_or_create(
                        profile=self.user.get_profile(), 
                        round_name=self.current_round,
                      )
    entry.points = top_entry.points + 1
    entry.last_awarded_submission = datetime.datetime.today() - datetime.timedelta(days=3)
    entry.save()

    self.assertEqual(ScoreboardEntry.user_round_overall_rank(self.user, self.current_round), 1, 
                    "Check user is ranked #1 for the current round.")

    user2 = User(username="test_user2", password="changeme")
    user2.save()

    profile2 = user2.get_profile()
    entry2, created = ScoreboardEntry.objects.get_or_create(
                        profile=profile2, 
                        round_name=self.current_round,
                      )
    entry2.points = entry.points
    entry2.last_awarded_submission = datetime.datetime.today()
    entry2.save()

    self.assertEqual(ScoreboardEntry.user_round_overall_rank(self.user, self.current_round), 2, 
                    "Check user is now second.")             
    
  def testUserFloorRoundRankWithPoints(self):
    """Tests that the floor rank calculation for a round is correct based on points."""
    # Setup dorm
    dorm = Dorm(name="Test dorm")
    dorm.save()
    floor = Floor(number="A", dorm=dorm)
    floor.save()
    
    profile = self.user.get_profile()
    profile.floor = floor
    profile.save()
    
    # Set up entry
    top_entry  = ScoreboardEntry.objects.filter(round_name=self.current_round).order_by("-points")[0]
    entry, created = ScoreboardEntry.objects.get_or_create(
                        profile=self.user.get_profile(), 
                        round_name=self.current_round,
                      )
    entry.points = top_entry.points + 1
    entry.last_awarded_submission = datetime.datetime.today()
    entry.save()
    
    self.assertEqual(ScoreboardEntry.user_round_floor_rank(self.user, self.current_round), 1, 
                    "Check user is ranked #1 for the current round.")
    
    user2 = User(username="test_user2", password="changeme")
    user2.save()
    profile2 = user2.get_profile()
    profile2.floor = floor
    profile2.save()
    
    entry2, created = ScoreboardEntry.objects.get_or_create(
                        profile=profile2, 
                        round_name=self.current_round,
                      )
    entry2.points = entry.points + 1
    entry2.last_awarded_submission = entry.last_awarded_submission
    entry2.save()
    
    self.assertEqual(ScoreboardEntry.user_round_floor_rank(self.user, self.current_round), 2, 
                    "Check user is now second.")
                    
  def testUserFloorRoundRankWithSubmissionDate(self):
    """Tests that the floor rank calculation for a round is correct based on points."""
    # Set up dorm
    dorm = Dorm(name="Test dorm")
    dorm.save()
    floor = Floor(number="A", dorm=dorm)
    floor.save()
    
    # Create the entry for the test user
    profile = self.user.get_profile()
    profile.floor = floor
    profile.save()
    top_entry  = ScoreboardEntry.objects.filter(round_name=self.current_round).order_by("-points")[0]
    entry, created = ScoreboardEntry.objects.get_or_create(
                        profile=self.user.get_profile(), 
                        round_name=self.current_round,
                      )
    entry.points = top_entry.points + 1
    entry.last_awarded_submission = datetime.datetime.today() - datetime.timedelta(days=3)
    entry.save()
    
    # Create another test user
    user2 = User(username="test_user2", password="changeme")
    user2.save()
    profile2 = user2.get_profile()
    profile2.floor = floor
    profile2.save()

    entry2, created = ScoreboardEntry.objects.get_or_create(
                        profile=profile2, 
                        round_name=self.current_round,
                      )
    entry2.points = entry.points
    entry2.last_awarded_submission = datetime.datetime.today()
    entry2.save()

    self.assertEqual(ScoreboardEntry.user_round_floor_rank(self.user, self.current_round), 2, 
                    "Check user is now second.")
                    
  def testRoundRankWithoutEntry(self):
    """Tests that the overall rank calculation is correct even if a user has not done anything yet."""
    dorm = Dorm(name="Test dorm")
    dorm.save()
    floor = Floor(number="A", dorm=dorm)
    floor.save()
    
    profile = self.user.get_profile()
    # Rank will be the number of users who have points plus one.
    overall_rank = Profile.objects.filter(points__gt=0).count() + 1
    floor_rank = Profile.objects.filter(points__gt=0, floor=floor).count() + 1

    self.assertEqual(ScoreboardEntry.user_round_overall_rank(self.user, self.current_round), overall_rank, 
                    "Check user is last overallfor the current round.")
    self.assertEqual(ScoreboardEntry.user_round_floor_rank(self.user, self.current_round), floor_rank, 
                    "Check user is last in their floor for the current round.")
                    
    user2 = User(username="test_user2", password="changeme")
    user2.save()

    profile2 = user2.get_profile()
    entry2, created = ScoreboardEntry.objects.get_or_create(
                        profile=profile2, 
                        round_name=self.current_round,
                      )
    entry2.points = 10
    entry2.last_awarded_submission = datetime.datetime.today()
    entry2.floor = floor
    entry2.save()

    self.assertEqual(ScoreboardEntry.user_round_overall_rank(self.user, self.current_round), overall_rank + 1, 
                    "Check that the user's overall rank has moved down.")
    self.assertEqual(ScoreboardEntry.user_round_floor_rank(self.user, self.current_round), floor_rank + 1, 
                    "Check that the user's floor rank has moved down.")
                    
  def tearDown(self):
    """Restore the saved settings."""
    settings.COMPETITION_ROUNDS = self.saved_rounds
    