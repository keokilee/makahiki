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
    
class ProfileUnitTests(TestCase):
  def testFloorRankWithPoints(self):
    """Tests that the floor_rank method accurately computes the rank based on points."""
    user = User(username="test_user", password="changeme")
    user.save()
    dorm = Dorm(name="Test dorm")
    dorm.save()
    floor = Floor(number="A", dorm=dorm)
    floor.save()
    
    profile = user.get_profile()
    profile.floor = floor
    
    # Check that the user is ranked last if they haven't done anything.
    rank = Profile.objects.filter(floor=floor, points__gt=profile.points).count() + 1
    self.assertEqual(profile.floor_rank(), rank, "Check that the user is ranked last.")
    
    # Make the user number 1 overall.
    top_user  = Profile.objects.all().order_by("-points")[0]
    profile.add_points(top_user.points + 1, datetime.datetime.today())
    profile.save()
    
    self.assertEqual(profile.floor_rank(), 1, "Check that the user is number 1.")
    
    user2 = User(username="test_user2", password="changeme")
    user2.save()
    
    profile2 = user2.get_profile()
    profile2.add_points(profile.points + 1, datetime.datetime.today())
    profile2.save()
    
    self.assertEqual(profile.floor_rank(), 1, 
                  "Check that the user is still number 1 if the new profile is not on the same floor.")
                  
    profile2.floor = floor
    profile2.save()
    
    self.assertEqual(profile.floor_rank(), 2, "Check that the user is now rank 2.")
    
  def testFloorRankWithSubmissionDate(self):
    """Tests that the floor_rank method accurately computes the rank when users have the same number of points."""
    user = User(username="test_user", password="changeme")
    user.save()
    dorm = Dorm(name="Test dorm")
    dorm.save()
    floor = Floor(number="A", dorm=dorm)
    floor.save()
    
    profile = user.get_profile()
    profile.floor = floor
    top_user  = Profile.objects.all().order_by("-points")[0]
    profile.add_points(top_user.points + 1, datetime.datetime.today())
    profile.save()
    
    self.assertEqual(profile.floor_rank(), 1, "Check that the user is number 1.")
    
    user2 = User(username="test_user2", password="changeme")
    user2.save()
    
    profile2 = user2.get_profile()
    profile2.add_points(profile.points, datetime.datetime.today())
    profile2.save()
                  
    profile2.floor = floor
    profile2.save()
    
    self.assertEqual(profile.floor_rank(), 2, "Check that the user is now rank 2.")
    
  def testOverallRankWithPoints(self):
    """Tests that the rank method accurately computes the rank with points."""
    user = User(username="test_user", password="changeme")
    user.save()
    profile = user.get_profile()
    
    # Check if the rank works if the user has done nothing.
    rank = Profile.objects.filter(points__gt=profile.points).count() + 1
    self.assertEqual(profile.overall_rank(), rank, "Check that the user is at least tied for last.")
    
    # Make the user ranked 1st.
    top_user  = Profile.objects.all().order_by("-points")[0]
    profile.add_points(top_user.points + 1, datetime.datetime.today())
    profile.save()
    
    self.assertEqual(profile.overall_rank(), 1, "Check that the user is number 1.")
    
    user2 = User(username="test_user2", password="changeme")
    user2.save()
    
    profile2 = user2.get_profile()
    profile2.add_points(profile.points + 1, datetime.datetime.today())
    profile2.save()
    
    self.assertEqual(profile.overall_rank(), 2, "Check that the user is now rank 2.")
    
  def testOverallRankWithSubmissionDate(self):
    """Tests that the overall_rank method accurately computes the rank when two users have the same number of points."""
    user = User(username="test_user", password="changeme")
    user.save()
    
    profile = user.get_profile()
    top_user  = Profile.objects.all().order_by("-points")[0]
    profile.add_points(top_user.points + 1, datetime.datetime.today() - datetime.timedelta(days=1))
    profile.save()
    
    self.assertEqual(profile.overall_rank(), 1, "Check that the user is number 1.")
    
    user2 = User(username="test_user2", password="changeme")
    user2.save()
    
    profile2 = user2.get_profile()
    profile2.add_points(profile.points, datetime.datetime.today())
    profile2.save()
    
    self.assertEqual(profile.overall_rank(), 2, "Check that the user is now rank 2.")
    
  def testOverallRankForCurrentRound(self):
    """Test that we can retrieve the rank for the user in the current round."""
    saved_rounds = settings.COMPETITION_ROUNDS
    current_round = "Round 1"
    start = datetime.date.today()
    end = start + datetime.timedelta(days=7)
    
    settings.COMPETITION_ROUNDS = {
      "Round 1" : {
        "start": start.strftime("%Y-%m-%d"),
        "end": end.strftime("%Y-%m-%d"),
      },
    }
    
    user = User(username="test_user", password="changeme")
    user.save()
    
    profile = user.get_profile()
    top_user  = Profile.objects.all().order_by("-points")[0]
    profile.add_points(top_user.points + 1, datetime.datetime.today())
    profile.save()
    
    self.assertEqual(profile.current_round_overall_rank(), 1, "Check that the user is number 1.")
    
    user2 = User(username="test_user2", password="changeme")
    user2.save()
    
    profile2 = user2.get_profile()
    profile2.add_points(profile.points + 1, datetime.datetime.today())
    profile2.save()
    
    self.assertEqual(profile.current_round_overall_rank(), 2, "Check that the user is now number 2.")
    
    # Restore saved rounds.
    settings.COMPETITION_ROUNDS = saved_rounds
    
  def testFloorRankForCurrentRound(self):
    """Test that we can retrieve the rank for the user in the current round."""
    saved_rounds = settings.COMPETITION_ROUNDS
    current_round = "Round 1"
    start = datetime.date.today()
    end = start + datetime.timedelta(days=7)

    settings.COMPETITION_ROUNDS = {
      "Round 1" : {
        "start": start.strftime("%Y-%m-%d"),
        "end": end.strftime("%Y-%m-%d"),
      },
    }
    
    dorm = Dorm(name="Test dorm")
    dorm.save()
    floor = Floor(number="A", dorm=dorm)
    floor.save()

    user = User(username="test_user", password="changeme")
    user.save()

    profile = user.get_profile()
    top_user  = Profile.objects.all().order_by("-points")[0]
    profile.add_points(top_user.points + 1, datetime.datetime.today())
    profile.floor = floor
    profile.save()

    self.assertEqual(profile.current_round_floor_rank(), 1, "Check that the user is number 1.")

    user2 = User(username="test_user2", password="changeme")
    user2.save()

    profile2 = user2.get_profile()
    profile2.add_points(profile.points + 1, datetime.datetime.today())
    profile2.floor = floor
    profile2.save()

    self.assertEqual(profile.current_round_floor_rank(), 2, "Check that the user is now number 2.")

    # Restore saved rounds.
    settings.COMPETITION_ROUNDS = saved_rounds
    
  def testCurrentRoundPoints(self):
    """Tests that we can retrieve the points for the user in the current round."""
    # Save the round information and set up a test round.
    saved_rounds = settings.COMPETITION_ROUNDS
    current_round = "Round 1"
    start = datetime.date.today()
    end = start + datetime.timedelta(days=7)

    settings.COMPETITION_ROUNDS = {
      "Round 1" : {
        "start": start.strftime("%Y-%m-%d"),
        "end": end.strftime("%Y-%m-%d"),
      },
    }

    user = User(username="test_user", password="changeme")
    user.save()

    profile = user.get_profile()
    points = profile.points
    profile.add_points(10, datetime.datetime.today())
    profile.save()

    self.assertEqual(profile.current_round_points(), points + 10, "Check that the user has 10 more points in the current round.")

    profile.add_points(10, datetime.datetime.today() - datetime.timedelta(days=1))

    self.assertEqual(profile.current_round_points(), points + 10, 
        "Check that the number of points did not change when points are awarded outside of a round.")

    # Restore saved rounds.
    settings.COMPETITION_ROUNDS = saved_rounds
    
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
    