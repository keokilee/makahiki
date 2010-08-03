import datetime

from django.test import TestCase
from django.conf import settings

from django.contrib.auth.models import User
from makahiki_profiles.models import Profile, ScoreboardEntry
from activities import *
from activities.models import Activity, ActivityMember, Commitment, CommitmentMember, Goal, GoalMember
from floors.models import Floor

class ActivitiesUnitTestCase(TestCase):
  fixtures = ["base_data.json", "user_data.json"]
  
  def setUp(self):
    """Set the competition settings to the current date for testing."""
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
  
  def testApproveAddsPoints(self):
    """Test for verifying that approving a user awards them points."""
    user = User.objects.all()[0]
    points = user.get_profile().points
    last_awarded_submission = user.get_profile().last_awarded_submission
    
    # Setup to check round points.
    entry = user.get_profile().scoreboardentry_set.get(round_name=self.current_round)
    round_points = entry.points
    round_last_awarded = entry.last_awarded_submission
    
    activity = Activity.objects.all()[0]
    activity_points = activity.point_value
    
    activity_member = ActivityMember(user=user, activity=activity)
    activity_member.save()
    
    # Verify that nothing has changed.
    self.assertEqual(points, user.get_profile().points)
    self.assertEqual(last_awarded_submission, user.get_profile().last_awarded_submission)
    entry = user.get_profile().scoreboardentry_set.get(round_name=self.current_round)
    self.assertEqual(round_points, entry.points)
    self.assertEqual(round_last_awarded, entry.last_awarded_submission)
    
    activity_member.approval_status = "approved"
    activity_member.save()
    
    # Verify overall score changed.
    new_points = user.get_profile().points
    self.assertEqual(new_points - points, activity_points)
    self.assertEqual(activity_member.submission_date, user.get_profile().last_awarded_submission)
    
    # Verify round score changed.
    entry = user.get_profile().scoreboardentry_set.get(round_name=self.current_round)
    self.assertEqual(round_points + activity_points, entry.points)
    self.assertTrue(abs(activity_member.submission_date - entry.last_awarded_submission) < datetime.timedelta(minutes=1))
    
  def testApprovePostsMessage(self):
    """Test that an approved activity posts to the user's wall."""
    floor = Floor.objects.all()[0]
    num_posts = floor.post_set.count()
    profile = floor.profile_set.all()[0]
    
    activity = Activity.objects.all()[0]
    
    activity_member = ActivityMember(user=profile.user, activity=activity)
    activity_member.approval_status = "approved"
    activity_member.save()
    
    self.assertTrue(num_posts == floor.post_set.count() - 1)
    
  def testUnapproveRemovesPoints(self):
    """Test that unapproving a user removes their points."""
    user = User.objects.all()[0]
    points = user.get_profile().points
    last_awarded_submission = user.get_profile().last_awarded_submission
    
    # Setup to check round points.
    entry = user.get_profile().scoreboardentry_set.get(round_name=self.current_round)
    round_points = entry.points
    round_last_awarded = entry.last_awarded_submission
    
    activity = Activity.objects.all()[0]
    
    activity_member = ActivityMember(user=user, activity=activity)
    activity_member.approval_status = "approved"
    activity_member.save()
    award_date = activity_member.award_date
    
    activity_member.approval_status = "rejected"
    activity_member.save()
    new_points = user.get_profile().points
    
    self.assertTrue(activity_member.award_date is None)
    self.assertEqual(points, new_points)
    self.assertTrue(user.get_profile().last_awarded_submission < award_date)
    
    entry = user.get_profile().scoreboardentry_set.get(round_name=self.current_round)
    self.assertEqual(round_points, entry.points)
    self.assertTrue(entry.last_awarded_submission is None or entry.last_awarded_submission < award_date)
    
  def testDeleteRemovesPoints(self):
    """Test that deleting an approved ActivityMember removes their points."""
    
    user = User.objects.all()[0]
    points = user.get_profile().points
    last_awarded_submission = user.get_profile().last_awarded_submission
    
    # Setup to check round points.
    entry = user.get_profile().scoreboardentry_set.get(round_name=self.current_round)
    round_points = entry.points
    round_last_awarded = entry.last_awarded_submission
    
    activity = Activity.objects.all()[0]
    
    activity_member = ActivityMember(user=user, activity=activity)
    activity_member.approval_status = "approved"
    activity_member.save()
    award_date = activity_member.award_date
    
    activity_member.delete()
    new_points = user.get_profile().points
    
    self.assertEqual(points, new_points)
    self.assertTrue(user.get_profile().last_awarded_submission < award_date)
    
    entry = user.get_profile().scoreboardentry_set.get(round_name=self.current_round)
    self.assertEqual(round_points, entry.points)
    self.assertTrue(entry.last_awarded_submission is None or entry.last_awarded_submission < award_date)
    
  def tearDown(self):
    """Restore the saved settings."""
    settings.COMPETITION_ROUNDS = self.saved_rounds
    
class ActivitiesFunctionalTestCase(TestCase):
  fixtures = ["base_data.json", "user_data.json"]
  
  def setUp(self):
    self.user = User.objects.get(username="user")
    self.client.post('/account/login/', {"username": self.user.username, "password": "changeme", "remember": False})
  
  def testLoadActivities(self):
    """Test that we can load the activity list page."""
    response = self.client.get('/activities/activity_list/')
    self.failUnlessEqual(response.status_code, 200)
    for activity in self.user.activity_set.all():
      self.assertNotIn(activity, response.context["available_items"])
      self.failUnless((activity in response.context["user_items"]) or (activity in response.context["completed_items"]))
      
  def testAddActivity(self):
    """Test that we can add an activity."""
    activity = Activity.objects.exclude(
      activitymember__user=self.user,
    )[0]
    response = self.client.post('/activities/add_activity/%d/' % activity.pk, {}, "multipart/form-data", True)
    self.assertRedirects(response, "/profiles/profile/%d/" % self.user.pk)
    self.failUnless(activity in response.context["user_activities"])
    response = self.client.get('/activities/activity_list/')
    self.failUnless(activity in response.context["user_items"])
    
  def testApprovedActivity(self):
    """Test that approved activities appear in the correct location."""
    activity = Activity.objects.exclude(
      activitymember__user=self.user,
    )[0]
    member = ActivityMember(user=self.user, activity=activity, approval_status="approved")
    member.save()
    response = self.client.get('/activities/activity_list/')
    self.failUnless(activity in response.context["completed_items"])
    
class CommitmentsUnitTestCase(TestCase):
  fixtures = ["base_data.json", "user_data.json"]
  
  def setUp(self):
    """Set the competition settings to the current date for testing."""
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
  
  def testCompletionAddsPoints(self):
    """Tests that completing a task adds points."""
    user = User.objects.all()[0]
    points = user.get_profile().points
    last_awarded_submission = user.get_profile().last_awarded_submission
    
    # Setup to check round points.
    entry = user.get_profile().scoreboardentry_set.get(round_name=self.current_round)
    round_points = entry.points
    round_last_awarded = entry.last_awarded_submission
    
    commitment = Commitment.objects.all()[0]
    commitment_member = CommitmentMember(user=user, commitment=commitment, completion_date=datetime.datetime.today())
    
    commitment_member.save()
    
    # Check that this does not change the user's points.
    self.assertTrue(points == user.get_profile().points)
    self.assertTrue(last_awarded_submission == user.get_profile().last_awarded_submission)
    
    entry = user.get_profile().scoreboardentry_set.get(round_name=self.current_round)
    self.assertEqual(round_points, entry.points)
    self.assertEqual(round_last_awarded, entry.last_awarded_submission)
    
    commitment_member.award_date = datetime.datetime.today()
    commitment_member.save()
    points += commitment_member.commitment.point_value
    self.assertTrue(points, user.get_profile().points)
    self.assertTrue(user.get_profile().last_awarded_submission == commitment_member.award_date)
    
    entry = user.get_profile().scoreboardentry_set.get(round_name=self.current_round)
    round_points += commitment_member.commitment.point_value
    self.assertEqual(round_points, entry.points)
    self.assertTrue(abs(entry.last_awarded_submission - commitment_member.award_date) < datetime.timedelta(minutes=1))
    
  def testAddCompletePostsMessages(self):
    """Test that an added commitment and a completed commitment posts to the user's wall."""
    floor = Floor.objects.all()[0]
    num_posts = floor.post_set.count()
    profile = floor.profile_set.all()[0]

    commitment = Commitment.objects.all()[0]
    commitment_member = CommitmentMember(user=profile.user, commitment=commitment, completion_date=datetime.datetime.today())
    commitment_member.save()
    self.assertEqual(floor.post_set.count() - num_posts, 1)
    
    commitment_member.award_date = datetime.datetime.today()
    commitment_member.save()
    self.assertEqual(floor.post_set.count() - num_posts, 2)
    
  def testDeleteRemovesPoints(self):
    """Test that deleting a commitment member after it is completed removes the user's points."""
    user = User.objects.all()[0]
    points = user.get_profile().points
    
    # Setup to check round points.
    entry = user.get_profile().scoreboardentry_set.get(round_name=self.current_round)
    round_points = entry.points
    round_last_awarded = entry.last_awarded_submission
    
    commitment = Commitment.objects.all()[0]
    commitment_member = CommitmentMember(user=user, commitment=commitment, completion_date=datetime.datetime.today())
    commitment_member.save()
    
    commitment_member.award_date = datetime.datetime.today()
    commitment_member.save()
    award_date = commitment_member.award_date
    commitment_member.delete()
    
    # Verify nothing has changed.
    # Slightly lenient since it depends on how data is dumped.
    profile = user.get_profile()
    self.assertTrue(profile.last_awarded_submission is None or profile.last_awarded_submission < award_date)
    self.assertEqual(points, profile.points)
    
    entry = user.get_profile().scoreboardentry_set.get(round_name=self.current_round)
    self.assertEqual(round_points, entry.points)
    self.assertTrue(entry.last_awarded_submission is None or entry.last_awarded_submission < award_date)
    
  def tearDown(self):
    """Restore the saved settings."""
    settings.COMPETITION_ROUNDS = self.saved_rounds

class CommitmentsFunctionalTestCase(TestCase):
  fixtures = ["base_data.json", "user_data.json"]
  
  def setUp(self):
    self.user = User.objects.get(username="user")
    self.client.post('/account/login/', {"username": self.user.username, "password": "changeme", "remember": False})
      
  def testAddCommitment(self):
    """Test that we can add a commitment."""
    
    commitment = get_available_commitments(self.user)[0]
    response = self.client.post('/activities/add_commitment/%d/' % commitment.pk, {}, "multipart/form-data", True)
    self.assertRedirects(response, "/profiles/profile/%d/" % self.user.pk)
    self.failUnless(commitment in response.context["user_commitments"])
    response = self.client.get('/activities/commitment_list/')
    self.failUnless(commitment in response.context["user_items"])
    
  def testCompleteCommitment(self):
    """Test that we can complete a commitment and get the points."""
    
    from activities.forms import CommitmentCommentForm
    
    points = self.user.get_profile().points
    commitment = get_available_commitments(self.user)[0]
    response = self.client.post('/activities/add_commitment/%d/' % commitment.pk, {}, "multipart/form-data", True)
    
    # Set the commitment to be completed today and request points.
    member = CommitmentMember.objects.get(commitment=commitment, user=self.user, completion_date__gt=datetime.date.today())
    member.completion_date = datetime.date.today()
    member.save()
    response = self.client.get('/activities/request_commitment_points/%d/' % commitment.pk)
    self.failUnlessEqual(response.status_code, 200)
    response = self.client.post('/activities/request_commitment_points/%d/' % commitment.pk)
    self.assertRedirects(response, "/profiles/profile/%d/" % self.user.pk)
    response = self.client.get("/profiles/profile/%d/" % self.user.pk)
    self.assertNotContains(response, "Either the commitment is not active or it is not completed yet.")

    response = self.client.get('/activities/commitment_list/')
    self.failUnless(commitment in response.context["completed_items"])
    
class GoalsUnitTestCase(TestCase):
  fixtures = ["base_data.json", "user_data.json"]
  
  def setUp(self):
    """Set the competition settings to the current date for testing."""
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
  
  def testCompletionAddsPoints(self):
    """Tests that completing a goal adds points to the entire floor."""
    floor = Floor.objects.all()[0]
    profiles = floor.profile_set.all().order_by("pk")
    scoreboard = ScoreboardEntry.objects.filter(profile__floor=floor, round_name=self.current_round).order_by("pk")
    scoreboard = list(scoreboard)
    user = profiles[0].user
    
    goal = Goal.objects.all()[0]
    goal_member = GoalMember(user=user, floor=floor, goal=goal)
    goal_member.save()
    
    # Verify that the item is not approved and that no points have been added.
    self.assertTrue(goal_member.approval_status == u'unapproved')
    self.assertTrue(goal_member.award_date is None)
    after_profiles = floor.profile_set.all().order_by("pk")
    after_scoreboard = ScoreboardEntry.objects.filter(profile__floor=floor, round_name=self.current_round).order_by("pk")
    for i in range(0, len(profiles)):
      self.assertEqual(profiles[i].points, after_profiles[i].points)
      self.assertEqual(profiles[i].last_awarded_submission, after_profiles[i].last_awarded_submission)
      self.assertEqual(scoreboard[i].points, after_scoreboard[i].points)
      self.assertEqual(scoreboard[i].last_awarded_submission, after_scoreboard[i].last_awarded_submission)
      
    goal_member.approval_status = 'approved'
    goal_member.save()
    
    self.assertTrue(goal_member.award_date is not None)
    
    # Verify that points are updated.
    after_profiles = floor.profile_set.all().order_by("pk")
    after_scoreboard = ScoreboardEntry.objects.filter(profile__floor=floor, round_name=self.current_round).order_by("pk")
    for i in range(0, len(profiles)):
      self.assertEqual(profiles[i].points + goal.point_value, after_profiles[i].points)
      self.assertEqual(scoreboard[i].points + goal.point_value, after_scoreboard[i].points)
      
      if profiles[i].last_awarded_submission is None:
        self.assertTrue(after_profiles[i].last_awarded_submission is not None)
      else:
        self.assertTrue(profiles[i].last_awarded_submission < after_profiles[i].last_awarded_submission)
        
      if scoreboard[i].last_awarded_submission is None:
        self.assertTrue(after_scoreboard[i].last_awarded_submission is not None)
      else:
        self.assertTrue(scoreboard[i].last_awarded_submission < after_scoreboard[i].last_awarded_submission)
       
  def testAddCompletePostsMessages(self):
    """Test that an added goal and a completed goal posts to the user's wall."""
    floor = Floor.objects.all()[0]
    profiles = floor.profile_set.all().order_by("pk")
    num_posts = floor.post_set.count()
    user = profiles[0].user
    
    goal = Goal.objects.all()[0]
    goal_member = GoalMember(user=user, floor=floor, goal=goal)
    goal_member.save()
    self.assertTrue(num_posts == floor.post_set.count() - 1)

    goal_member.approval_status = 'approved'
    goal_member.save()
    self.assertTrue(num_posts == floor.post_set.count() - 2) 
    
  def testUnapproveRemovesPoints(self):
    """Tests that unapproving an approved goal removes points from members of the entire floor."""
    floor = Floor.objects.all()[0]
    profiles = floor.profile_set.all().order_by("pk")
    scoreboard = ScoreboardEntry.objects.filter(profile__floor=floor, round_name=self.current_round).order_by("profile")
    user = profiles[0].user
    
    goal = Goal.objects.all()[0]
    goal_member = GoalMember(user=user, floor=floor, goal=goal)
    goal_member.approval_status = 'approved'
    goal_member.save()
    
    goal_member.approval_status = 'rejected'
    goal_member.save()
    
    self.assertTrue(goal_member.award_date is None)
    after_profiles = floor.profile_set.all().order_by("pk")
    after_scoreboard = ScoreboardEntry.objects.filter(profile__floor=floor, round_name=self.current_round).order_by("profile")
    for i in range(0, len(profiles)):
      self.assertEqual(profiles[i].points, after_profiles[i].points)
      self.assertEqual(scoreboard[i].points, after_scoreboard[i].points)
      self.assertEqual(profiles[i].last_awarded_submission, after_profiles[i].last_awarded_submission)
      self.assertEqual(scoreboard[i].last_awarded_submission, after_scoreboard[i].last_awarded_submission)
      
  def testDeleteRemovesPoints(self):
    """Tests that deleting an approved goal removes points from members of the entire floor."""
    floor = Floor.objects.all()[0]
    profiles = floor.profile_set.all().order_by("pk")
    scoreboard = ScoreboardEntry.objects.filter(profile__floor=floor, round_name=self.current_round).order_by("profile")
    user = profiles[0].user
    
    goal = Goal.objects.all()[0]
    goal_member = GoalMember(user=user, floor=floor, goal=goal)
    goal_member.approval_status = 'approved'
    goal_member.save()
    goal_member.delete()
    
    after_profiles = floor.profile_set.all().order_by("pk")
    after_scoreboard = ScoreboardEntry.objects.filter(profile__floor=floor, round_name=self.current_round).order_by("profile")
    for i in range(0, len(profiles)):
      self.assertEqual(profiles[i].points, after_profiles[i].points)
      self.assertEqual(scoreboard[i].points, after_scoreboard[i].points)
      self.assertEqual(profiles[i].last_awarded_submission, after_profiles[i].last_awarded_submission)
      self.assertEqual(scoreboard[i].last_awarded_submission, after_scoreboard[i].last_awarded_submission)
      
  def tearDown(self):
    """Restore the saved settings."""
    settings.COMPETITION_ROUNDS = self.saved_rounds
