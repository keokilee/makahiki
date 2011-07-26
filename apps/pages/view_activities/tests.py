import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.conf import settings

from django.contrib.auth.models import User
from components.floors.models import Floor
from components.activities.models import Commitment, Activity, ActivityMember, ConfirmationCode
from components.quests.models import Quest

class ActivitiesFunctionalTestCase(TestCase):
  fixtures = ["base_floors.json"]
  def setUp(self):
    self.user = User.objects.create_user("user", "user@test.com", password="changeme")
    floor = Floor.objects.all()[0]
    profile = self.user.get_profile()
    profile.floor = floor
    profile.setup_complete = True
    profile.setup_profile = True
    profile.save()
    
    self.client.login(username="user", password="changeme")
  
  def testIndex(self):
    """Check that we can load the index page."""
    response = self.client.get(reverse("activity_index"))
    self.failUnlessEqual(response.status_code, 200)
    
  def testScoreboard(self):
    """Test that the scoreboard loads current round information."""
    saved_rounds = settings.COMPETITION_ROUNDS
    start = datetime.date.today()
    end = start + datetime.timedelta(days=7)
    
    settings.COMPETITION_ROUNDS = {
      "Round 1" : {
        "start": start.strftime("%Y-%m-%d"),
        "end": end.strftime("%Y-%m-%d"),
      },
    }
    
    # Give the user points in the round and then check the queryset used in the page.
    profile = self.user.get_profile()
    profile.add_points(10, datetime.datetime.today())
    profile.save()
    
    response = self.client.get(reverse("activity_index"))
    self.assertContains(response, "Round 1 Points Scoreboard", count=1,
        msg_prefix="This should display the current round scoreboard.")
    self.assertEqual(response.context["floor_standings"][0], profile.floor,
        "The user's floor should be leading.")
    self.assertEqual(response.context["profile_standings"][0], profile,
        "The user's should be leading the overall standings.")
    self.assertEqual(response.context["user_floor_standings"][0], profile,
        "The user should be leading in their own floor.")   
    self.assertEqual(response.context["floor_standings"][0].points, 10,
        "The user's floor should have 10 points this round.")
    self.assertEqual(response.context["profile_standings"][0].current_round_points(), 10,
        "The user should have 10 points this round.")
    self.assertEqual(response.context["user_floor_standings"][0].current_round_points(), 10,
        "The user should have 10 points this round.")
        
    # Get points outside of the round and see if affects the standings.
    profile.add_points(10, datetime.datetime.today() - datetime.timedelta(days=2))
    profile.save()
    
    response = self.client.get(reverse("activity_index"))
    self.assertEqual(response.context["floor_standings"][0].points, 10,
        "Test that the user's floor still has 10 points.")
    self.assertEqual(response.context["profile_standings"][0].current_round_points(), 10,
        "The user still should have 10 points this round.")
    self.assertEqual(response.context["user_floor_standings"][0].current_round_points(), 10,
        "The user still should have 10 points this round.")
        
    # Try without a round.
    settings.COMPETITION_ROUNDS = {}
    
    response = self.client.get(reverse("activity_index"))
    self.assertContains(response, "Overall Points Scoreboard", count=1,
        msg_prefix="This should display the overall scoreboard.")
    self.assertEqual(response.context["floor_standings"][0].points, 20,
        "The user's floor should have 20 points overall.")
    self.assertEqual(response.context["profile_standings"][0].current_round_points(), 20,
        "The user should have 20 points overall.")
    self.assertEqual(response.context["user_floor_standings"][0].current_round_points(), 20,
        "The user should have 20 points overall.")
    
    # Don't forget to clean up.
    settings.COMPETITION_ROUNDS = saved_rounds
    
  def testConfirmationCode(self):
    """
    Tests the submission of a confirmation code.
    """
    activity = Activity(
        title="Test activity",
        slug="test-activity",
        description="Testing!",
        duration=10,
        point_value=10,
        pub_date=datetime.datetime.today(),
        expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
        confirm_type="code",
        type="event",
        event_date=datetime.datetime.today() - datetime.timedelta(days=1, seconds=30),
    )
    activity.save()
    
    ConfirmationCode.generate_codes_for_activity(activity, 10)
    code = ConfirmationCode.objects.filter(activity=activity)[0]
    
    response = self.client.post(reverse("activity_add_task", args=("event", "test-activity")), {
        "response": code.code,
        "code": 1,
    }, follow=True)
    
    self.failUnlessEqual(response.status_code, 200)
    self.assertEqual(ConfirmationCode.objects.filter(activity=activity, is_active=False).count(), 1)
    code = ConfirmationCode.objects.filter(activity=activity)[0]
    self.assertTrue(activity in self.user.activity_set.filter(activitymember__award_date__isnull=False))
    
    # Try submitting the code again and check if we have an error message.
    code = ConfirmationCode.objects.filter(activity=activity)[1]
    response = self.client.post(reverse("activity_add_task", args=("event", "test-activity")), {
        "response": code.code,
        "code": 1,
    }, follow=True)
    self.assertContains(response, "You have already redemmed a code for this activity.")
    
    # Try creating a new activity with codes and see if we can submit a code for one activity for another.
    code = ConfirmationCode.objects.filter(activity=activity)[2]
    activity = Activity(
        title="Test activity 2",
        slug="test-activity2",
        description="Testing!",
        duration=10,
        point_value=10,
        pub_date=datetime.datetime.today(),
        expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
        confirm_type="code",
        type="event",
        event_date=datetime.datetime.today() - datetime.timedelta(days=1, seconds=30),
    )
    activity.save()
    ConfirmationCode.generate_codes_for_activity(activity, 1)
    
    response = self.client.post(reverse("activity_add_task", args=("event", "test-activity2")), {
        "response": code.code,
        "code": 1,
    }, follow=True)
    self.assertContains(response, "This confirmation code is not valid for this activity.")
    
  def testRejectedActivity(self):
    """
    Test that a rejected activity submission posts a message.
    """
    activity = Activity(
        title="Test activity",
        description="Testing!",
        duration=10,
        point_value=10,
        pub_date=datetime.datetime.today(),
        expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
        confirm_type="text",
        type="activity",
    )
    activity.save()
    member = ActivityMember(activity=activity, user=self.user, approval_status="rejected")
    member.save()
    response = self.client.get(reverse("activity_index"))
    self.assertContains(response, "Your response to <a href='%s'>%s</a> was not approved" % (
        reverse("activity_task", args=(activity.type, activity.slug,)),
        activity.title,
    ))
    response = self.client.get(reverse("activity_index"))
    self.assertNotContains(response, "notification-box")
    
  def testAddCommitment(self):
    """
    Test that the user can add a commitment.
    """
    commitment = Commitment(
        title="Test commitment",
        slug="test-commitment",
        description="A commitment!",
        point_value=10,
        type="commitment",
    )
    commitment.save()
    
    response = self.client.post(reverse("activity_add_task", args=(commitment.type, commitment.slug,)), follow=True)
    self.failUnlessEqual(response.status_code, 200)
    