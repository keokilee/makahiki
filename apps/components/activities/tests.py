import datetime

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail

from components.activities import *
from components.activities.models import *
from components.makahiki_notifications.models import UserNotification

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
                      type="activity",
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
    
  def testCanopyActivityLog(self):
    """
    Test that canopy activities create the appropriate log.
    """
    self.activity.is_canopy = True
    self.activity.save()
    member = ActivityMember(user=self.user, activity=self.activity, approval_status='approved')
    member.save()
    
    # Check the points log for this user.
    log = self.user.pointstransaction_set.all()[0]
    self.assertTrue(log.message.startswith('Canopy'))
    
  def testActivityLog(self):
    """
    Test that regular activities create the appropriate log.
    """
    member = ActivityMember(user=self.user, activity=self.activity, approval_status='approved')
    member.save()

    # Check the points log for this user.
    log = self.user.pointstransaction_set.all()[0]
    self.assertTrue(log.message.startswith(self.activity.type.capitalize()))
    
  def testPopularActivities(self):
    """Check which activity is the most popular."""
    activity_member = ActivityMember(user=self.user, activity=self.activity)
    activity_member.approval_status = "approved"
    activity_member.save()
    
    activities = get_popular_activities()
    self.assertEqual(activities[0]["title"], self.activity.title)
    self.assertEqual(activities[0]["completions"], 1, "Most popular activity should have one completion.")
    
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
                  type="activity"
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
    self.activity.type = "event"
    self.activity.depends_on = "True"
    self.activity.name = "name"
    self.activity.pub_date=datetime.datetime.today()
    self.activity.expire_date=datetime.datetime.today() + datetime.timedelta(days=7)
    self.activity.event_date = datetime.datetime.today()
    
    self.activity.save()
    
    activities = get_available_activities(self.user)
    if self.activity in activities:
      self.fail("Event is listed in the activity list.")
        
    events = get_available_events(self.user)
    
    if self.activity.id != events[0]["id"]:
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
    
    activity_member = ActivityMember(user=self.user, activity=self.activity, submission_date=datetime.datetime.today())
    activity_member.approval_status = "approved"
    activity_member.save()
    award_date = activity_member.award_date
    
    activity_member.approval_status = "rejected"
    activity_member.save()
    new_points = self.user.get_profile().points
    self.assertEqual(len(mail.outbox), 1, "Check that the rejection sent an email.")
    
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
    
  def testRejectionNotifications(self):
    """
    Test that notifications are created by rejections and 
    are marked as read when the member changes back to pending.
    """
    notifications = UserNotification.objects.count()
    activity_member = ActivityMember(user=self.user, activity=self.activity, submission_date=datetime.datetime.today())
    activity_member.approval_status = "rejected"
    activity_member.submission_date = datetime.datetime.today()
    activity_member.save()
    
    self.assertEqual(UserNotification.objects.count(), notifications + 1, 
        "New notification should have been created.")
    notice = activity_member.notifications.all()[0]
    self.assertTrue(notice.unread, "Notification should be unread.")
        
    activity_member.approval_status = "pending"
    activity_member.save()
    
    notice = activity_member.notifications.all()[0]
    self.assertFalse(notice.unread, "Notification should be marked as read.")
    
  def tearDown(self):
    """Restore the saved settings."""
    settings.COMPETITION_ROUNDS = self.saved_rounds
    
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
  
  def testPopularCommitments(self):
    """Tests that we can retrieve the most popular commitments."""
    commitment_member = CommitmentMember(user=self.user, commitment=self.commitment)
    commitment_member.award_date = datetime.datetime.today()
    commitment_member.save()
    
    commitments = get_popular_commitments()
    self.assertEqual(commitments[0]["title"], self.commitment.title)
    self.assertEqual(commitments[0]["completions"], 1, "Most popular commitment should have one completion.")
    
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
    
class RemindersUnitTestCase(TestCase):
  def setUp(self):
    """
    Create a test event and a test user.
    """
    self.event = Activity.objects.create(
        title="Test event",
        slug="test-event",
        description="Testing!",
        duration=10,
        point_value=10,
        pub_date=datetime.datetime.today(),
        expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
        confirm_type="text",
        type="event",
        event_date=datetime.datetime.today() + datetime.timedelta(days=1),
    )
    
    self.user = User.objects.create_user("testuser", "test@test.com")
    
  def testSendEmailReminder(self):
    """Test that we can send an email reminder."""
    reminder = EmailReminder.objects.create(
        user=self.user,
        activity=self.event,
        email_address="test@tester.com",
        send_at=datetime.datetime.today(),
    )
    
    reminder.send()
    sent_mail = mail.outbox[0]
    self.assertTrue("test@tester.com" in sent_mail.to, "Email address should be in the recipient list.")
    reminder = self.user.emailreminder_set.get(activity=self.event)
    self.assertTrue(reminder.sent, "Reminder should be marked as sent.")
    
    # Try to send the reminder again.
    mail_count = len(mail.outbox)
    reminder.send()
    self.assertEqual(len(mail.outbox), mail_count, "A duplicate email should not be sent.")
    
  def testSendAttTextReminder(self):
    """
    Test that we construct the appropriate email address for AT&T customers.
    """
    reminder = TextReminder.objects.create(
        user=self.user,
        activity=self.event,
        text_number="808-555-1234",
        text_carrier="att",
        send_at=datetime.datetime.today(),
    )
    
    reminder.send()
    sent_mail = mail.outbox[0]
    att_email = "8085551234@txt.att.net"
    self.assertTrue(att_email in sent_mail.to, "AT&T email address should be in the recipient list.")
    
    mail_count = len(mail.outbox)
    reminder.send()
    self.assertEqual(len(mail.outbox), mail_count, "A duplicate email should not be sent.")
    
  def testSendTmobileTextReminder(self):
    """
    Test that we construct the appropriate email address for T-Mobile customers.
    """
    reminder = TextReminder.objects.create(
        user=self.user,
        activity=self.event,
        text_number="808-555-1234",
        text_carrier="tmobile",
        send_at=datetime.datetime.today(),
    )
    
    reminder.send()
    sent_mail = mail.outbox[0]
    tmobile_mail = "8085551234@tmomail.net"
    self.assertTrue(tmobile_mail in sent_mail.to, "T-Mobile email address should be in the recipient list.")
    
  def testSendSprintTextReminder(self):
    """
    Test that we construct the appropriate email address for Sprint customers.
    """
    reminder = TextReminder.objects.create(
        user=self.user,
        activity=self.event,
        text_number="808-555-1234",
        text_carrier="sprint",
        send_at=datetime.datetime.today(),
    )

    reminder.send()
    sent_mail = mail.outbox[0]
    sprint_mail = "8085551234@messaging.sprintpcs.com"
    self.assertTrue(sprint_mail in sent_mail.to, "Sprint email address should be in the recipient list.")
    
  def testSendVerizonTextReminder(self):
    """
    Test that we construct the appropriate email address for Verizon customers.
    """
    reminder = TextReminder.objects.create(
        user=self.user,
        activity=self.event,
        text_number="808-555-1234",
        text_carrier="verizon",
        send_at=datetime.datetime.today(),
    )

    reminder.send()
    sent_mail = mail.outbox[0]
    tmobile_mail = "8085551234@vtext.com"
    self.assertTrue(tmobile_mail in sent_mail.to, "Verizon email address should be in the recipient list.")
