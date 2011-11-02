import datetime

from django.conf import settings
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.db import IntegrityError

from components.activities.models import Activity, ActivityMember
from components.floors.models import Dorm, Floor
from components.makahiki_profiles.models import Profile, PointsTransaction

class ProfileLeadersTests(TestCase):
  def setUp(self):
    self.users = [User.objects.create_user("test%d" % i, "test@test.com") for i in range(0, 3)]
    
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
    
  def testLeadersInRound(self):
    """
    Test that we can retrieve the leaders in a given round.
    """
    # Test one user
    profile = self.users[0].get_profile()
    profile.add_points(10, datetime.datetime.today() - datetime.timedelta(minutes=1), "Test")
    profile.save()
    
    self.assertEqual(Profile.points_leaders(round_name=self.current_round)[0], profile, 
        "Current leader is not the leading user.")
    
    # Have another user move ahead in points
    profile2 = self.users[1].get_profile()
    profile2.add_points(profile.points + 1, datetime.datetime.today(), "Test")
    profile2.save()
    
    self.assertEqual(Profile.points_leaders(round_name=self.current_round)[0], profile2, 
        "User 2 should be the leading profile.")
    
    # Have this user get the same amount of points, but an earlier award date.
    profile3 = self.users[2].get_profile()
    profile3.add_points(profile2.points, datetime.datetime.today() - datetime.timedelta(minutes=1), "Test")
    profile3.save()
    
    self.assertEqual(Profile.points_leaders(round_name=self.current_round)[0], profile2, 
        "User 2 should still be the leading profile.")
    
    # Have the first user earn more points outside of the round.
    profile.add_points(2, datetime.datetime.today() - datetime.timedelta(days=2), "Test")
    profile.save()
    
    self.assertEqual(Profile.points_leaders(round_name=self.current_round)[0], profile2, 
        "User 2 should still be the leading profile.")
        
  def testLeadersOverall(self):
    """
    Test that we can retrieve the leaders in a given round.
    """
    # Test one user
    profile = self.users[0].get_profile()
    profile.add_points(10, datetime.datetime.today() - datetime.timedelta(minutes=1), "Test")
    profile.save()

    self.assertEqual(Profile.points_leaders()[0], profile, 
        "Current leader is not the leading user.")

    # Have another user move ahead in points
    profile2 = self.users[1].get_profile()
    profile2.add_points(profile.points + 1, datetime.datetime.today(), "Test")
    profile2.save()

    self.assertEqual(Profile.points_leaders()[0], profile2, 
        "User 2 should be the leading profile.")

    # Have this user get the same amount of points, but an earlier award date.
    profile3 = self.users[2].get_profile()
    profile3.add_points(profile2.points, datetime.datetime.today() - datetime.timedelta(minutes=1), "Test")
    profile3.save()

    self.assertEqual(Profile.points_leaders()[0], profile2, 
        "User 2 should still be the leading profile.")
    
  def tearDown(self):
    """Restore the saved settings."""
    settings.COMPETITION_ROUNDS = self.saved_rounds
    
class ProfileUnitTests(TestCase):
  def testDisplayNameUnique(self):
    user1 = User(username="test_user", password="changeme")
    user1.save()
    user2 = User(username="test_user1", password="changeme")
    user2.save()
    
    profile1 = user1.get_profile()
    profile1.name = "Test User"
    profile1.save()
    
    profile2 = user2.get_profile()
    profile2.name = "Test User"
    self.assertRaises(IntegrityError, profile2.save)
    
  def testReferralBonus(self):
    """
    Test that the referral bonus is awarded once the referred user reaches 30 points.
    """
    user1 = User.objects.create_user("test_user", 'user@test.com', password="changeme")
    user1.save()
    user2 = User.objects.create_user('test_user2', 'user2@test.com', password="changeme")
    user2.save()
    
    profile1 = user1.get_profile()
    profile1.setup_profile = True
    profile1.setup_complete = True
    points1 = profile1.points
    profile1.save()
    
    profile2 = user2.get_profile()
    profile2.setup_profile = True
    profile2.setup_complete = True
    profile2.referring_user = user1
    profile2.add_points(10, datetime.datetime.today(), 'test 1')
    profile2.save()
    
    self.assertEqual(points1, Profile.objects.get(user=user1).points, 'User 1 should not have received any points.')
    
    profile2.add_points(20, datetime.datetime.today(), 'Trigger referral bonus.')
    points2 = profile2.points
    profile2.save()
    
    self.assertEqual(points1 + 10, Profile.objects.get(user=user1).points, 'User 1 should have the referral bonus')
    self.assertEqual(points2 + 10, Profile.objects.get(user=user2).points, 'User 2 should have the referral bonus')
    self.assertTrue(Profile.objects.get(user=user2).referrer_awarded, 'User 2 should have the referral awarded.')
    
    profile2.add_points(20, datetime.datetime.today(), 'Post test')
    profile2.save()
    
    self.assertEqual(points1 + 10, Profile.objects.get(user=user1).points, 'User 1 should not be given the referral bonus again.')
    
  def testReferralLoop(self):
    user1 = User.objects.create_user("test_user", 'user@test.com', password="changeme")
    user1.save()
    user2 = User.objects.create_user('test_user2', 'user2@test.com', password="changeme")
    user2.save()
    
    profile1 = user1.get_profile()
    profile1.setup_profile = True
    profile1.setup_complete = True
    profile1.referring_user = user2
    profile1.add_points(25, datetime.datetime.today(), 'test 1')
    profile1.save()
    
    profile2 = user2.get_profile()
    profile2.setup_profile = True
    profile2.setup_complete = True
    profile2.referring_user = user1
    profile2.add_points(25, datetime.datetime.today(), 'test 1')
    profile2.save()
    
    profile1.add_points(10, datetime.datetime.today(), 'test 1')
    profile1.save()
    
    # for log in user1.pointstransaction_set.all():
    #   print log.message
      
    self.assertEqual(Profile.objects.get(user=user1).points, 55)
    self.assertEqual(Profile.objects.get(user=user2).points, 45)
    
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
    profile.add_points(top_user.points + 1, datetime.datetime.today(), "Test")
    profile.save()
    
    self.assertEqual(profile.floor_rank(), 1, "Check that the user is number 1.")
    
    user2 = User(username="test_user2", password="changeme")
    user2.save()
    
    profile2 = user2.get_profile()
    profile2.add_points(profile.points + 1, datetime.datetime.today(), "Test")
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
    profile.add_points(top_user.points + 1, datetime.datetime.today() - datetime.timedelta(minutes=1), "Test")
    profile.save()
    
    self.assertEqual(profile.floor_rank(), 1, "Check that the user is number 1.")
    
    user2 = User(username="test_user2", password="changeme")
    user2.save()
    
    profile2 = user2.get_profile()
    profile2.add_points(profile.points, datetime.datetime.today(), "Test")
    profile2.save()
                  
    profile2.floor = floor
    profile2.save()
    print profile.points
    print profile2.points
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
    profile.add_points(top_user.points + 1, datetime.datetime.today(), "Test")
    profile.save()
    
    self.assertEqual(profile.overall_rank(), 1, "Check that the user is number 1.")
    
    user2 = User(username="test_user2", password="changeme")
    user2.save()
    
    profile2 = user2.get_profile()
    profile2.add_points(profile.points + 1, datetime.datetime.today(), "Test")
    profile2.save()
    
    self.assertEqual(profile.overall_rank(), 2, "Check that the user is now rank 2.")
    
  def testOverallRankWithSubmissionDate(self):
    """Tests that the overall_rank method accurately computes the rank when two users have the same number of points."""
    user = User(username="test_user", password="changeme")
    user.save()
    
    profile = user.get_profile()
    top_user  = Profile.objects.all().order_by("-points")[0]
    profile.add_points(top_user.points + 1, datetime.datetime.today() - datetime.timedelta(days=1), "Test")
    profile.save()
    
    self.assertEqual(profile.overall_rank(), 1, "Check that the user is number 1.")
    
    user2 = User(username="test_user2", password="changeme")
    user2.save()
    
    profile2 = user2.get_profile()
    profile2.add_points(profile.points, datetime.datetime.today(), "Test")
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
    profile.add_points(top_user.points + 1, datetime.datetime.today(), "Test")
    profile.save()
    
    self.assertEqual(profile.current_round_overall_rank(), 1, "Check that the user is number 1.")
    
    user2 = User(username="test_user2", password="changeme")
    user2.save()
    
    profile2 = user2.get_profile()
    profile2.add_points(profile.points + 1, datetime.datetime.today(), "Test")
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
    profile.add_points(top_user.points + 1, datetime.datetime.today(), "Test")
    profile.floor = floor
    profile.save()

    self.assertEqual(profile.current_round_floor_rank(), 1, "Check that the user is number 1.")

    user2 = User(username="test_user2", password="changeme")
    user2.save()

    profile2 = user2.get_profile()
    profile2.add_points(profile.points + 1, datetime.datetime.today(), "Test")
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
    profile.add_points(10, datetime.datetime.today(), "Test")
    profile.save()

    self.assertEqual(profile.current_round_points(), points + 10, "Check that the user has 10 more points in the current round.")

    profile.add_points(10, datetime.datetime.today() - datetime.timedelta(days=1), "Test")

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
                slug="test-activity",
                description="Testing!",
                duration=10,
                point_value=10,
                pub_date=datetime.datetime.today(),
                expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
                confirm_type="text",
                type="activity",
    )
    activity1.save()
    
    activity2 = Activity(
                title="Test activity 2",
                slug="test-activity-2",
                description="Testing!",
                duration=10,
                point_value=15,
                pub_date=datetime.datetime.today(),
                expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
                confirm_type="text",
                type="activity",
    )
    activity2.save()
    activities = [activity1, activity2]
    
    # Submit the first activity.  This is what we're going to rollback to.
    activity_member = ActivityMember(user=user, activity=activities[0], submission_date=datetime.datetime.today())
    activity_member.approval_status = "approved"
    activity_member.submission_date = datetime.datetime.today() - datetime.timedelta(days=1)
    activity_member.save()
    
    points = user.get_profile().points
    submit_date = user.get_profile().last_awarded_submission
    
    # Submit second activity.
    activity_member = ActivityMember(user=user, activity=activities[1], submission_date=datetime.datetime.today())
    activity_member.approval_status = "approved"
    activity_member.submission_date = datetime.datetime.today()
    activity_member.save()
    logs = user.pointstransaction_set.count()
    
    activity_member.approval_status = "rejected"
    activity_member.submission_date = datetime.datetime.today()
    activity_member.save()
    
    # Verify that we rolled back to the previous activity.
    self.assertEqual(points, user.get_profile().points)
    # TODO: Rolling back last awarded submission is broken.  May be fixed when we implement
    # a points transaction log.
    # self.assertTrue(abs(submit_date - user.get_profile().last_awarded_submission) < datetime.timedelta(minutes=1))
