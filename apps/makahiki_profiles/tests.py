import datetime

from django.conf import settings
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from activities.models import Activity, ActivityMember
from floors.models import Floor
from makahiki_profiles.models import Profile, ScoreboardEntry
    
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
    
    activity_points = self.activity.point_value

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
    
class ProfilesFunctionalTestCase(TestCase):
  fixtures = ["base_data.json", "user_data.json"]
  
  def testProfileEdit(self):
    """Test to check that the user can edit their profile."""
    
    user = User.objects.get(username="user")
    self.client.post('/account/login/', {"username": user.username, "password": "changeme", "remember": False})
    response = self.client.get(reverse("profile_edit"))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "makahiki_profiles/profile_edit.html", "Check user can access profile edit.")
    response = self.client.post(reverse("profile_edit"), {
                  "theme": "default", 
                  "name": "test",
                  "about": "Testing test test."
                }, follow=True)
    self.assertRedirects(response, reverse("profile_detail", args=(user.get_profile().pk,)), 
                         msg_prefix="Check the user is redirected to their page.")
    self.assertContains(response, "Testing test test.", msg_prefix="Check that the info is saved.")
    
  def testUnauthenticatedAccess(self):
    """Test that an unauthenticated user cannot access user profiles."""
    profile = Profile.objects.all()[0]
    response = self.client.get(reverse("profile_detail", args=(profile.pk,)))
    self.assertTemplateUsed(response, "restricted.html", msg_prefix="Test that user cannot access a user's profile page.")
    
  def testUserProfileAccess(self):
    """Test that a user can only access their own page and pages of those on their floor."""
    
    user = User.objects.get(username="user")
    self.client.post('/account/login/', {"username": user.username, "password": "changeme", "remember": False})
    
    # Check that the user can access their own page.
    profile = user.get_profile()
    response = self.client.get(reverse("profile_detail", args=(profile.pk,)))
    self.assertTemplateUsed(response, "makahiki_profiles/profile.html", msg_prefix="Test that user can access their own page.")
    
    # Check that the user can access their fellow floor member's page.
    floor = profile.floor
    profile = floor.profile_set.exclude(user=user)[0]
    response = self.client.get(reverse("profile_detail", args=(profile.pk,)))
    self.assertTemplateUsed(response, "makahiki_profiles/profile.html", 
            msg_prefix="Test that user can access a fellow floor member's page.")
    
    # Check that the user cannot access the profile page of a member of another floor.
    floor = Floor.objects.exclude(pk=floor.pk)[0]
    profile = floor.profile_set.all()[0]
    response = self.client.get(reverse("profile_detail", args=(profile.pk,)))
    self.assertTemplateUsed(response, "restricted.html", 
            msg_prefix="Test that user cannot access the profile page of a user in another floor.")
            
  def testAdminAccess(self):
    """Test that an admin can access any user's page."""
    
    self.client.post('/account/login/', {"username": "admin", "password": "changeme", "remember": False})
    profile = Profile.objects.exclude(user__username="admin", floor=None)[0]
    response = self.client.get(reverse("profile_detail", args=(profile.pk,)))
    self.assertTemplateUsed(response, "makahiki_profiles/profile.html", 
            msg_prefix="Test that admin can access a member's page.")

  def testLoadProfile(self):
    """Test that we can load the profile page and the boxes are correct."""
    
    self.user = User.objects.get(username="user")
    self.client.post('/account/login/', {"username": self.user.username, "password": "changeme", "remember": False})
    
    response = self.client.get('/profiles/profile/%s/' % self.user.pk)
    
    # Verify standings are correct.
    self.assertEqual(len(response.context["standings_titles"]), len(response.context["floor_standings"]))
    
    activities = self.user.activity_set.filter(activitymember__award_date=None)
    commitments = self.user.commitment_set.filter(commitmentmember__award_date=None)
    goals = self.user.get_profile().floor.goal_set.filter(goalmember__award_date=None)
    
    self.assertEqual(len(activities), len(response.context["user_activities"]))
    for activity in activities:
      self.assertTrue(activity in response.context["user_activities"])
      
    self.assertEqual(len(commitments), len(response.context["user_commitments"]))
    for commitment in commitments:
      self.assertTrue(commitment in response.context["user_commitments"])
      
    self.assertEqual(len(goals), len(response.context["user_goals"]))
    for goal in goals:
      self.assertTrue(goal in response.context["user_goals"])
      
  def testSelectedTab(self):
    """Test that the current round's tab is selected."""
    
    self.user = User.objects.get(username="user")
    self.client.post('/account/login/', {"username": self.user.username, "password": "changeme", "remember": False})
    
    # Set up rounds for test.
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
    
    response = self.client.get('/profiles/profile/%s/' % self.user.pk)
    self.assertEqual(0, response.context["selected_tab"])
    
    start = end
    end = end + datetime.timedelta(days=7)
    settings.COMPETITION_ROUNDS = {
      "Round 1" : {
        "start": start.strftime("%Y-%m-%d"),
        "end": end.strftime("%Y-%m-%d"),
      },
    }
    
    response = self.client.get('/profiles/profile/%s/' % self.user.pk)
    self.assertEqual(1, response.context["selected_tab"])
    
    # Restore settings.
    settings.COMPETITION_ROUNDS = self.saved_rounds