import datetime

from django.test import TestCase

from django.contrib.auth.models import User
from makahiki_profiles.models import Profile
from activities.models import Activity, ActivityMember, Commitment, CommitmentMember, Goal, GoalMember
from floors.models import Floor

class ActivitiesUnitTestCase(TestCase):
  fixtures = ["base_data.json", "user_data.json"]
  
  def testApproveAddsPoints(self):
    """Test for verifying that approving a user awards them points."""
    user = User.objects.all()[0]
    points = user.get_profile().points
    last_awarded_submission = user.get_profile().last_awarded_submission
    
    activity = Activity.objects.all()[0]
    activity_points = activity.point_value
    
    activity_member = ActivityMember(user=user, activity=activity)
    activity_member.save()
    
    # Verify that nothing has changed.
    self.assertTrue(points == user.get_profile().points)
    self.assertTrue(last_awarded_submission == user.get_profile().last_awarded_submission)
    
    activity_member.approval_status = "approved"
    activity_member.save()
    
    new_points = user.get_profile().points
    self.assertTrue(new_points - points == activity_points)
    self.assertTrue(activity_member.submission_date == user.get_profile().last_awarded_submission)
    
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
    
    activity = Activity.objects.all()[0]
    
    activity_member = ActivityMember(user=user, activity=activity)
    activity_member.approval_status = "approved"
    activity_member.save()
    award_date = activity_member.award_date
    
    activity_member.approval_status = "rejected"
    activity_member.save()
    new_points = user.get_profile().points
    
    self.assertTrue(activity_member.award_date is None)
    self.assertTrue(points == new_points)
    self.assertTrue(user.get_profile().last_awarded_submission < award_date)
    
  def testDeleteRemovesPoints(self):
    """Test that deleting an approved ActivityMember removes their points."""
    
    user = User.objects.all()[0]
    points = user.get_profile().points
    last_awarded_submission = user.get_profile().last_awarded_submission
    
    activity = Activity.objects.all()[0]
    
    activity_member = ActivityMember(user=user, activity=activity)
    activity_member.approval_status = "approved"
    activity_member.save()
    award_date = activity_member.award_date
    
    activity_member.delete()
    new_points = user.get_profile().points
    
    self.assertTrue(points == new_points)
    self.assertTrue(user.get_profile().last_awarded_submission < award_date)
    
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
  
  def testCompletionAddsPoints(self):
    """Tests that completing a task adds points."""
    user = User.objects.all()[0]
    points = user.get_profile().points
    last_awarded_submission = user.get_profile().last_awarded_submission
    
    commitment = Commitment.objects.all()[0]
    commitment_member = CommitmentMember(user=user, commitment=commitment, completion_date=datetime.datetime.today())
    
    commitment_member.save()
    
    # Check that this does not change the user's points.
    self.assertTrue(points == user.get_profile().points)
    self.assertTrue(last_awarded_submission == user.get_profile().last_awarded_submission)
    
    commitment_member.award_date = datetime.datetime.today()
    commitment_member.save()
    points += commitment_member.commitment.point_value
    self.assertTrue(points, user.get_profile().points)
    self.assertTrue(user.get_profile().last_awarded_submission == commitment_member.award_date)
    
  def testAddCompletePostsMessages(self):
    """Test that an added commitment and a completed commitment posts to the user's wall."""
    floor = Floor.objects.all()[0]
    num_posts = floor.post_set.count()
    profile = floor.profile_set.all()[0]

    commitment = Commitment.objects.all()[0]
    commitment_member = CommitmentMember(user=profile.user, commitment=commitment, completion_date=datetime.datetime.today())
    commitment_member.save()
    self.assertTrue(floor.post_set.count() - num_posts == 1)
    
    commitment_member.award_date = datetime.datetime.today()
    commitment_member.save()
    self.assertTrue(floor.post_set.count() - num_posts == 2)
    
  def testDeleteRemovesPoints(self):
    """Test that deleting a commitment member after it is completed removes the user's points."""
    user = User.objects.all()[0]
    points = user.get_profile().points
    
    commitment = Commitment.objects.all()[0]
    commitment_member = CommitmentMember(user=user, commitment=commitment, completion_date=datetime.datetime.today())
    commitment_member.save()
    
    commitment_member.award_date = datetime.datetime.today()
    commitment_member.save()
    award_date = commitment_member.award_date
    commitment_member.delete()
    self.assertTrue(user.get_profile().last_awarded_submission < award_date)
    self.assertTrue(points == user.get_profile().points)
    
class GoalsUnitTestCase(TestCase):
  fixtures = ["base_data.json", "user_data.json"]
  
  def testCompletionAddsPoints(self):
    """Tests that completing a goal adds points to the entire floor."""
    floor = Floor.objects.all()[0]
    profiles = floor.profile_set.all().order_by("pk")
    user = profiles[0].user
    
    goal = Goal.objects.all()[0]
    goal_member = GoalMember(user=user, floor=floor, goal=goal)
    goal_member.save()
    
    # Verify that the item is not approved and that no points have been added.
    self.assertTrue(goal_member.approval_status == u'unapproved')
    self.assertTrue(goal_member.award_date is None)
    after_profiles = floor.profile_set.all().order_by("pk")
    for i in range(0, len(profiles)):
      self.assertTrue(profiles[i].points == after_profiles[i].points)
      self.assertTrue(profiles[i].last_awarded_submission == after_profiles[i].last_awarded_submission)
      
    goal_member.approval_status = 'approved'
    goal_member.save()
    
    self.assertTrue(goal_member.award_date is not None)
    # Verify that points are updated.
    after_profiles = floor.profile_set.all().order_by("pk")
    for i in range(0, len(profiles)):
      self.assertTrue(profiles[i].points + goal.point_value == after_profiles[i].points)
      if profiles[i].last_awarded_submission is None:
        self.assertTrue(after_profiles[i].last_awarded_submission is not None)
      else:
        self.assertTrue(profiles[i].last_awarded_submission < after_profiles[i].last_awarded_submission)
       
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
    user = profiles[0].user
    
    goal = Goal.objects.all()[0]
    goal_member = GoalMember(user=user, floor=floor, goal=goal)
    goal_member.approval_status = 'approved'
    goal_member.save()
    
    goal_member.approval_status = 'rejected'
    goal_member.save()
    
    self.assertTrue(goal_member.award_date is None)
    after_profiles = floor.profile_set.all().order_by("pk")
    for i in range(0, len(profiles)):
      self.assertTrue(profiles[i].points == after_profiles[i].points)
      self.assertTrue(profiles[i].last_awarded_submission == after_profiles[i].last_awarded_submission)
      
  def testDeleteRemovesPoints(self):
    """Tests that deleting an approved goal removes points from members of the entire floor."""
    floor = Floor.objects.all()[0]
    profiles = floor.profile_set.all().order_by("pk")
    user = profiles[0].user
    
    goal = Goal.objects.all()[0]
    goal_member = GoalMember(user=user, floor=floor, goal=goal)
    goal_member.approval_status = 'approved'
    goal_member.save()
    goal_member.delete()
    
    after_profiles = floor.profile_set.all().order_by("pk")
    for i in range(0, len(profiles)):
      self.assertTrue(profiles[i].points == after_profiles[i].points)
      self.assertTrue(profiles[i].last_awarded_submission == after_profiles[i].last_awarded_submission)
