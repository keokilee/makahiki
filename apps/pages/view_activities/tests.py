import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.conf import settings

from django.contrib.auth.models import User
from components.floors.models import Floor
from components.makahiki_profiles.models import Profile
from components.activities.models import *
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
    profile.add_points(10, datetime.datetime.today(), "test")
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
    profile.add_points(10, datetime.datetime.today() - datetime.timedelta(days=2), "test")
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
        slug="test-activity",
        duration=10,
        point_value=10,
        pub_date=datetime.datetime.today(),
        expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
        confirm_type="text",
        type="activity",
    )
    activity.save()
    member = ActivityMember(
        activity=activity, 
        user=self.user, 
        approval_status="rejected",
        submission_date=datetime.datetime.today(),
    )
    member.save()
    response = self.client.get(reverse("activity_index"))
    self.assertContains(response, "Your response to <a href='%s'>%s</a>" % (
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

    points = Profile.objects.get(user=self.user).points
    response = self.client.post(reverse("activity_add_task", args=(commitment.type, commitment.slug,)), follow=True)
    self.failUnlessEqual(response.status_code, 200)

    self.assertEqual(points, Profile.objects.get(user=self.user).points)

  def testMobileRedirect(self):
    """Tests that the mobile redirection and the cookie that forces the desktop version."""
    category = Category.objects.create(
        name="test category",
        slug="test-category",
    )
    commitment = Commitment(
        title="Test commitment",
        slug="test-commitment",
        description="A commitment!",
        point_value=10,
        type="commitment",
        category=category,
    )
    commitment.save()
    
    response = self.client.get(reverse("activity_task", args=(commitment.type, commitment.slug)),
        HTTP_USER_AGENT="Mozilla/5.0 (iPod; U; CPU like Mac OS X; en) AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/3A100a",
        follow=True
    )
    # self.failUnlessEqual(response.status_code, 302, "Mobile device should redirect.")
    self.assertTemplateUsed(response, "mobile/smartgrid/index.html")

    self.client.cookies['mobile-desktop'] = True

    response = self.client.get(reverse("activity_task", args=(commitment.type, commitment.slug)),
        HTTP_USER_AGENT="Mozilla/5.0 (iPod; U; CPU like Mac OS X; en) AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/3A100a",
        follow=True
    )
    # self.failUnlessEqual(response.status_code, 200, "Mobile device should not redirect.")
    self.assertTemplateUsed(response, "view_activities/index.html")
    
  def testAddEmailReminder(self):
    """
    Test that the user can create a email reminder.
    """
    event = Activity(
        title="Test event",
        slug="test-event",
        description="Testing!",
        duration=10,
        point_value=10,
        pub_date=datetime.datetime.today(),
        expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
        confirm_type="code",
        type="event",
        event_date=datetime.datetime.today() + datetime.timedelta(days=1),
    )
    event.save()
    
    reminders = self.user.emailreminder_set.count()
    
    # Test invalid forms
    response = self.client.post(reverse("activity_reminder", args=(event.type, event.slug,)), {
        "send_email": True,
        "email": "",
        "email_advance": "1",
        "send_text": False,
        "text_advance": "1",
    }, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    self.failUnlessEqual(response.status_code, 200)
    self.assertContains(response, "A valid email address is required.", 
        count=1, msg_prefix="Error text should be displayed.")
    self.assertEqual(self.user.emailreminder_set.count(), reminders, "Should not have added a reminder")
    
    response = self.client.post(reverse("activity_reminder", args=(event.type, event.slug,)), {
        "send_email": True,
        "email": "foo",
        "email_advance": "1",
        "send_text": False,
        "text_advance": "1",
    }, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    self.failUnlessEqual(response.status_code, 200)
    self.assertContains(response, "A valid email address is required.", 
        count=1, msg_prefix="Error text should be displayed.")
    self.assertEqual(self.user.emailreminder_set.count(), reminders, "Should not have added a reminder")
    
    # Test valid form
    response = self.client.post(reverse("activity_reminder", args=(event.type, event.slug,)), {
        "send_email": True,
        "email": "foo@test.com",
        "email_advance": "1",
        "send_text": False,
        "text_advance": "1",
    }, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    self.failUnlessEqual(response.status_code, 200)
    profile = Profile.objects.get(user=self.user)
    self.assertEqual(profile.contact_email, "foo@test.com", "Profile should now have a contact email.")
    self.assertEqual(self.user.emailreminder_set.count(), reminders + 1, "Should have added a reminder")
    
  def testChangeEmailReminder(self):
    """
    Test that we can adjust a reminder.
    """
    event = Activity(
        title="Test event",
        slug="test-event",
        description="Testing!",
        duration=10,
        point_value=10,
        pub_date=datetime.datetime.today(),
        expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
        confirm_type="code",
        type="event",
        event_date=datetime.datetime.today() + datetime.timedelta(days=1),
    )
    event.save()
    
    original_date = event.event_date - datetime.timedelta(hours=2)
    reminder = EmailReminder(
        user=self.user,
        activity=event,
        email_address="foo@foo.com",
        send_at=original_date,
    )
    reminder.save()
    reminder_count = self.user.emailreminder_set.count()
    
    response = self.client.post(reverse("activity_reminder", args=(event.type, event.slug,)), {
        "send_email": True,
        "email": "foo@test.com",
        "email_advance": "1",
        "send_text": False,
        "text_advance": "1",
    }, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    self.failUnlessEqual(response.status_code, 200)
    
    reminder = self.user.emailreminder_set.get(activity=event)
    profile = Profile.objects.get(user=self.user)
    self.assertEqual(reminder.email_address, "foo@test.com", "Email address should have changed.")
    self.assertEqual(profile.contact_email, "foo@test.com", "Profile email address should have changed.")
    self.assertNotEqual(reminder.send_at, original_date, "Send time should have changed.")
    self.assertEqual(self.user.emailreminder_set.count(), reminder_count, "No new reminders should have been created.")
    
  def testRemoveEmailReminder(self):
    """
    Test that unchecking send_email will remove the reminder.
    """
    event = Activity(
        title="Test event",
        slug="test-event",
        description="Testing!",
        duration=10,
        point_value=10,
        pub_date=datetime.datetime.today(),
        expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
        confirm_type="code",
        type="event",
        event_date=datetime.datetime.today() + datetime.timedelta(days=1),
    )
    event.save()
    
    reminder = EmailReminder(
        user=self.user,
        activity=event,
        email_address="foo@foo.com",
        send_at=event.event_date - datetime.timedelta(hours=2),
    )
    reminder.save()
    reminder_count = self.user.emailreminder_set.count()
    
    response = self.client.post(reverse("activity_reminder", args=(event.type, event.slug,)), {
        "send_email": False,
        "email": "",
        "email_advance": "1",
        "send_text": False,
        "text_advance": "1",
    }, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    self.failUnlessEqual(response.status_code, 200)
    
    self.assertEqual(self.user.emailreminder_set.count(), reminder_count - 1, "User should not have a reminder.")
    
  def testAddTextReminder(self):
    """
    Test that a user can create a text reminder.
    """
    event = Activity(
        title="Test event",
        slug="test-event",
        description="Testing!",
        duration=10,
        point_value=10,
        pub_date=datetime.datetime.today(),
        expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
        confirm_type="code",
        type="event",
        event_date=datetime.datetime.today() + datetime.timedelta(days=1),
    )
    event.save()
    
    reminders = self.user.textreminder_set.count()
    
    # Test invalid forms
    response = self.client.post(reverse("activity_reminder", args=(event.type, event.slug,)), {
        "send_email": False,
        "email": "",
        "email_advance": "1",
        "send_text": True,
        "text_number": "",
        "text_carrier": "att",
        "text_advance": "1",
    }, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    self.failUnlessEqual(response.status_code, 200)
    self.assertContains(response, "A valid phone number is required.", 
        count=1, msg_prefix="Error text should be displayed.")
    self.assertEqual(self.user.textreminder_set.count(), reminders, "Should not have added a reminder")
    
    response = self.client.post(reverse("activity_reminder", args=(event.type, event.slug,)), {
        "send_email": False,
        "email": "",
        "email_advance": "1",
        "send_text": True,
        "text_number": "555",
        "text_carrier": "att",
        "text_advance": "1",
    }, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    self.failUnlessEqual(response.status_code, 200)
    self.assertContains(response, "A valid phone number is required.", 
        count=1, msg_prefix="Error text should be displayed.")
    self.assertEqual(self.user.textreminder_set.count(), reminders, "Should not have added a reminder")
    
    # Test valid form
    response = self.client.post(reverse("activity_reminder", args=(event.type, event.slug,)), {
        "send_email": False,
        "email": "",
        "email_advance": "1",
        "send_text": True,
        "text_number": "808-555-1234",
        "text_carrier": "att",
        "text_advance": "1",
    }, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    
    self.failUnlessEqual(response.status_code, 200)
    self.assertEqual(self.user.textreminder_set.count(), reminders + 1, "Should have added a reminder")
    profile = Profile.objects.get(user=self.user)
    self.assertEqual(profile.contact_text, "808-555-1234", "Check that the user now has a contact number.")
    self.assertEqual(profile.contact_carrier, "att", "Check that the user now has a contact carrier.")
    
  def testChangeTextReminder(self):
    """
    Test that we can adjust a text reminder.
    """
    event = Activity(
        title="Test event",
        slug="test-event",
        description="Testing!",
        duration=10,
        point_value=10,
        pub_date=datetime.datetime.today(),
        expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
        confirm_type="code",
        type="event",
        event_date=datetime.datetime.today() + datetime.timedelta(days=1),
    )
    event.save()
    
    original_date = event.event_date - datetime.timedelta(hours=2)
    reminder = TextReminder(
        user=self.user,
        activity=event,
        text_number="8085551234",
        text_carrier="att",
        send_at=original_date,
    )
    reminder.save()
    reminder_count = self.user.textreminder_set.count()

    response = self.client.post(reverse("activity_reminder", args=(event.type, event.slug,)), {
        "send_email": False,
        "email": "",
        "email_advance": "1",
        "send_text": True,
        "text_number": "18085556789",
        "text_carrier": "sprint",
        "text_advance": "1",
    }, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    
    self.failUnlessEqual(response.status_code, 200)
    reminder = self.user.textreminder_set.get(activity=event)
    # print profile.contact_text
    profile = Profile.objects.get(user=self.user)
    self.assertEqual(reminder.text_number, "808-555-6789", "Text number should have updated.")
    self.assertEqual(profile.contact_text, "808-555-6789", "Profile text number should have updated.")
    self.assertNotEqual(reminder.send_at, original_date, "Send time should have changed.")
    self.assertEqual(self.user.textreminder_set.count(), reminder_count, "No new reminders should have been created.")
    
  def testRemoveTextReminder(self):
    """
    Test that we can adjust a text reminder.
    """
    event = Activity(
        title="Test event",
        slug="test-event",
        description="Testing!",
        duration=10,
        point_value=10,
        pub_date=datetime.datetime.today(),
        expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
        confirm_type="code",
        type="event",
        event_date=datetime.datetime.today() + datetime.timedelta(days=1),
    )
    event.save()

    reminder = TextReminder(
        user=self.user,
        activity=event,
        text_number="8085551234",
        text_carrier="att",
        send_at=event.event_date - datetime.timedelta(hours=2),
    )
    reminder.save()
    reminder_count = self.user.textreminder_set.count()

    response = self.client.post(reverse("activity_reminder", args=(event.type, event.slug,)), {
        "send_email": False,
        "email": "",
        "email_advance": "1",
        "send_text": False,
        "text_number": "",
        "text_carrier": "sprint",
        "text_advance": "1",
    }, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

    self.failUnlessEqual(response.status_code, 200)
    self.assertEqual(self.user.textreminder_set.count(), reminder_count - 1, "User should not have a reminder.")