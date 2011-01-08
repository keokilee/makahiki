import datetime

from django.test import TestCase
from django.conf import settings

from django.contrib.auth.models import User
from components.activities import *
from components.activities.models import Activity, ActivityMember, Commitment, CommitmentMember

class ActivitiesUnitTestCase(TestCase):
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
    
  def testActivityOrdering(self):
    """Check the ordering of two activities.  If they do not have priorities, they should be alphabetical."""
    activity2 = Activity(
                  title="Another test activity",
                  description="Testing!",
                  duration=10,
                  point_value=10,
                  pub_date=datetime.datetime.today(),
                  expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
                  confirm_type="text",
                )
    activity2.save()
    
    activities = get_available_activities(self.user)
    self.assertTrue(self.activity in activities, "Check that the first activity is in the list.")
    self.assertTrue(activity2 in activities, "Check that the second activity is in the list.")
    self.assertEqual(activities[0], activity2, "Check that the activities are ordered alphabetically.")
    
    # Add priority to test activity.
    self.activity.priority = 1
    self.activity.save()
    
    activities = get_available_activities(self.user)
    self.assertTrue(self.activity in activities, "Check that the first activity is in the list.")
    self.assertTrue(activity2 in activities, "Check that the second activity is in the list.")
    self.assertEqual(activities[0], self.activity, "Check that the test activity is now first.")
    
  def testGetEvents(self):
    """Verify that get_available_activities does not retrieve events."""
    self.activity.is_event = True
    self.activity.save()
    
    activities = get_available_activities(self.user)
    if self.activity in activities:
      self.fail("Event is listed in the activity list.")
        
    events = get_available_events(self.user)
    if not self.activity in events:
      self.fail("Event is not listed in the events list.")
  
  def testApproveAddsPoints(self):
    """Test for verifying that approving a user awards them points."""
    points = self.user.get_profile().points
    last_awarded_submission = self.user.get_profile().last_awarded_submission
    
    # Setup to check round points.
    (entry, created) = self.user.get_profile().scoreboardentry_set.get_or_create(round_name=self.current_round)
    round_points = entry.points
    round_last_awarded = entry.last_awarded_submission
    
    activity_points = self.activity.point_value
    
    activity_member = ActivityMember(user=self.user, activity=self.activity)
    activity_member.save()
    
    # Verify that nothing has changed.
    self.assertEqual(points, self.user.get_profile().points)
    self.assertEqual(last_awarded_submission, self.user.get_profile().last_awarded_submission)
    entry = self.user.get_profile().scoreboardentry_set.get(round_name=self.current_round)
    self.assertEqual(round_points, entry.points)
    self.assertEqual(round_last_awarded, entry.last_awarded_submission)
    
    activity_member.approval_status = "approved"
    activity_member.save()
    
    # Verify overall score changed.
    new_points = self.user.get_profile().points
    self.assertEqual(new_points - points, activity_points)
    self.assertEqual(activity_member.submission_date, self.user.get_profile().last_awarded_submission)
    
    # Verify round score changed.
    entry = self.user.get_profile().scoreboardentry_set.get(round_name=self.current_round)
    self.assertEqual(round_points + activity_points, entry.points)
    self.assertTrue(abs(activity_member.submission_date - entry.last_awarded_submission) < datetime.timedelta(minutes=1))
    
  def testUnapproveRemovesPoints(self):
    """Test that unapproving a user removes their points."""
    points = self.user.get_profile().points
    
    # Setup to check round points.
    (entry, created) = self.user.get_profile().scoreboardentry_set.get_or_create(round_name=self.current_round)
    round_points = entry.points
    
    activity_member = ActivityMember(user=self.user, activity=self.activity)
    activity_member.approval_status = "approved"
    activity_member.save()
    award_date = activity_member.award_date
    
    activity_member.approval_status = "rejected"
    activity_member.save()
    new_points = self.user.get_profile().points
    
    self.assertTrue(activity_member.award_date is None)
    self.assertEqual(points, new_points)
    self.assertTrue(self.user.get_profile().last_awarded_submission is None)
    
    entry = self.user.get_profile().scoreboardentry_set.get(round_name=self.current_round)
    self.assertEqual(round_points, entry.points)
    self.assertTrue(entry.last_awarded_submission is None or entry.last_awarded_submission < award_date)
    
  def testDeleteRemovesPoints(self):
    """Test that deleting an approved ActivityMember removes their points."""
    
    points = self.user.get_profile().points
    
    # Setup to check round points.
    (entry, created) = self.user.get_profile().scoreboardentry_set.get_or_create(round_name=self.current_round)
    round_points = entry.points
    
    activity_member = ActivityMember(user=self.user, activity=self.activity)
    activity_member.approval_status = "approved"
    activity_member.save()
    award_date = activity_member.award_date
    
    activity_member.delete()
    new_points = self.user.get_profile().points
    
    self.assertEqual(points, new_points)
    self.assertTrue(self.user.get_profile().last_awarded_submission is None)
    
    entry = self.user.get_profile().scoreboardentry_set.get(round_name=self.current_round)
    self.assertEqual(round_points, entry.points)
    self.assertTrue(entry.last_awarded_submission is None or entry.last_awarded_submission < award_date)
    
  def testCreateVariablePointActivity(self):
    """Tests the creation of activities with variable points."""
    activity = Activity(
                title="Test activity",
                description="Variable points!",
                duration=10,
                point_range_start=5,
                point_range_end=10,
                pub_date=datetime.datetime.today(),
                expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
                confirm_type="text",
    )
    activity.save()
    self.assertTrue(activity.has_variable_points)
    
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
    self.assertTrue(response.context["available_events"] is not None)
    for activity in self.user.activity_set.all():
      self.assertNotIn(activity, response.context["available_items"])
      self.failUnless((activity in response.context["user_items"]) or (activity in response.context["completed_items"]))
      
  def testAddActivity(self):
    """Test that a user can add an activity."""
    activity = Activity.objects.exclude(
      activitymember__user=self.user,
    )[0]
    response = self.client.post('/activities/add_activity/%d/' % activity.pk, {}, "multipart/form-data", True)
    self.assertRedirects(response, "/profiles/profile/%d/" % self.user.pk)
    activities = [member.activity for member in response.context["user_activities"]]
    self.failUnless(activity in activities)
    response = self.client.get('/activities/activity_list/')
    activities = [member.activity for member in response.context["user_members"]]
    self.failUnless(activity in activities)
    
  def testRequestActivityPoints(self):
    """Test that we can get to the form for getting points."""
    activity = Activity.objects.exclude(
      activitymember__user=self.user,
    )[0]
    response = self.client.get('/activities/request_activity_points/%d/' % activity.pk)
    self.assertTemplateUsed(response, "activities/request_activity_points.html")
    
  def testApprovedActivity(self):
    """Test that approved activities appear in the correct location."""
    activity = Activity.objects.exclude(
      activitymember__user=self.user,
    )[0]
    floor = self.user.get_profile().floor
    num_posts = floor.post_set.count()
    
    member = ActivityMember(user=self.user, activity=activity, approval_status="approved")
    member.save()
    
    response = self.client.get('/activities/activity_list/')
    self.failUnless(activity in response.context["completed_items"])
    
    self.assertEqual(floor.post_set.count(), num_posts + 1)
    
class CommitmentsUnitTestCase(TestCase):
  def setUp(self):
    """Create test user and commitment. Set the competition settings to the current date for testing."""
    self.user = User(username="test_user", password="changeme")
    self.user.save()
    self.commitment = Commitment(
                title="Test commitment",
                description="A commitment!",
                point_value=10,
    )
    self.commitment.save()
    
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
    points = self.user.get_profile().points
    last_awarded_submission = self.user.get_profile().last_awarded_submission
    
    # Setup to check round points.
    (entry, created) = self.user.get_profile().scoreboardentry_set.get_or_create(round_name=self.current_round)
    round_points = entry.points
    round_last_awarded = entry.last_awarded_submission
    
    commitment_member = CommitmentMember(user=self.user, commitment=self.commitment, completion_date=datetime.datetime.today())
    commitment_member.save()
    
    # Check that this does not change the user's points.
    self.assertEqual(points, self.user.get_profile().points)
    self.assertEqual(last_awarded_submission, self.user.get_profile().last_awarded_submission)
    
    entry = self.user.get_profile().scoreboardentry_set.get(round_name=self.current_round)
    self.assertEqual(round_points, entry.points)
    self.assertEqual(round_last_awarded, entry.last_awarded_submission)
    
    commitment_member.award_date = datetime.datetime.today()
    commitment_member.save()
    points += commitment_member.commitment.point_value
    self.assertEqual(points, self.user.get_profile().points)
    self.assertEqual(self.user.get_profile().last_awarded_submission, commitment_member.award_date)
    
    entry = self.user.get_profile().scoreboardentry_set.get(round_name=self.current_round)
    round_points += commitment_member.commitment.point_value
    self.assertEqual(round_points, entry.points)
    self.assertTrue(abs(entry.last_awarded_submission - commitment_member.award_date) < datetime.timedelta(minutes=1))
    
  def testDeleteRemovesPoints(self):
    """Test that deleting a commitment member after it is completed removes the user's points."""
    points = self.user.get_profile().points
    
    # Setup to check round points.
    (entry, created) = self.user.get_profile().scoreboardentry_set.get_or_create(round_name=self.current_round)
    round_points = entry.points
    
    commitment_member = CommitmentMember(user=self.user, commitment=self.commitment, completion_date=datetime.datetime.today())
    commitment_member.save()
    
    commitment_member.award_date = datetime.datetime.today()
    commitment_member.save()
    award_date = commitment_member.award_date
    commitment_member.delete()
    
    # Verify nothing has changed.
    profile = self.user.get_profile()
    self.assertTrue(profile.last_awarded_submission is None or profile.last_awarded_submission < award_date)
    self.assertEqual(points, profile.points)
    
    entry = self.user.get_profile().scoreboardentry_set.get(round_name=self.current_round)
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
    commitments = [member.commitment for member in response.context["user_commitments"]]
    self.failUnless(commitment in commitments)
    response = self.client.get('/activities/commitment_list/')
    commitments = [member.commitment for member in response.context["user_members"]]
    self.failUnless(commitment in commitments)
    
  def testCompleteCommitment(self):
    """Test that we can complete a commitment and get the points."""
    
    from activities.forms import CommitmentCommentForm
    
    points = self.user.get_profile().points
    floor = self.user.get_profile().floor
    num_posts = floor.post_set.count()
    commitment = get_available_commitments(self.user)[0]
    commitment_count = len(get_available_commitments(self.user))
    response = self.client.post('/activities/add_commitment/%d/' % commitment.pk, {}, "multipart/form-data", True)
    
    # Set the commitment to be completed today and request points.
    member = CommitmentMember.objects.get(
        commitment=commitment, 
        user=self.user, 
        completion_date__gt=datetime.date.today(),
        award_date=None,
    )
    member.completion_date = datetime.date.today()
    member_id = member.id
    member.save()
    
    # Check that the added commitment generates a post.
    self.assertEqual(floor.post_set.count(), num_posts + 1)
    
    response = self.client.get('/activities/request_commitment_points/%d/' % commitment.pk)
    self.failUnlessEqual(response.status_code, 200)
    response = self.client.post('/activities/request_commitment_points/%d/' % commitment.pk)
    self.assertRedirects(response, "/profiles/profile/%d/" % self.user.pk)
    response = self.client.get("/profiles/profile/%d/" % self.user.pk)
    self.assertNotContains(response, "Either the commitment is not active or it is not completed yet.")
    
    member = CommitmentMember.objects.get(pk=member_id)
    self.assertTrue(member.award_date is not None, "Test that the commitment is awarded.")
    
    response = self.client.get('/activities/commitment_list/')
    self.failUnless(commitment in response.context["completed_items"])
    
    # Check that the commitment is available.
    self.assertEqual(commitment_count, len(get_available_commitments(self.user)), "Check for same number of commitments.")
    self.failUnless(commitment in response.context["available_items"])
    
    # Check that the completed commitment generates a post.
    self.assertEqual(floor.post_set.count(), num_posts + 2)
    
  def testMultipleCompleteCommitment(self):
    """Test that we can complete a commitment multiple times."""
    
    floor = self.user.get_profile().floor
    commitment = get_available_commitments(self.user)[0]
    response = self.client.post('/activities/add_commitment/%d/' % commitment.pk, {}, "multipart/form-data", True)

    # Set the commitment to be completed today and request points.
    member = CommitmentMember.objects.get(
        commitment=commitment, 
        user=self.user, 
        completion_date__gt=datetime.date.today(),
        award_date=None,
    )
    member.completion_date = datetime.date.today()
    member.save()
    
    # Complete the first time.
    response = self.client.post('/activities/request_commitment_points/%d/' % commitment.pk)
    
    # Now let's add and complete it again.
    response = self.client.post('/activities/add_commitment/%d/' % commitment.pk, {}, "multipart/form-data", True)
    member = CommitmentMember.objects.get(
        commitment=commitment, 
        user=self.user, 
        completion_date__gt=datetime.date.today(),
        award_date=None,
    )
    member.completion_date = datetime.date.today()
    member.save()
    
    # Complete the second time.
    response = self.client.post('/activities/request_commitment_points/%d/' % commitment.pk)
    self.assertRedirects(response, "/profiles/profile/%d/" % self.user.pk)
    response = self.client.get("/profiles/profile/%d/" % self.user.pk)
    self.assertNotContains(response, "Either the commitment is not active or it is not completed yet.")
    
    response = self.client.get('/activities/commitment_list/')
    self.failUnless(commitment in response.context["completed_items"])
    self.failUnless(commitment in response.context["available_items"])
