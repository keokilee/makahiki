import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from lib.brabeion import badges

from components.activities.models import Activity, ActivityMember, Commitment, CommitmentMember
from components.quests import get_quests, has_task, num_activities_completed, badge_awarded, possibly_completed_quests
from components.quests.models import Quest, QuestMember

class QuestTest(TestCase):
  def setUp(self):
    self.user = User(username="testuser", password="password")
    self.user.save()
    
  def testGetQuests(self):
    """Tests that we can get the quests for a user."""
    # Create some sample quests.
    self.assertEqual(get_quests(self.user).count(), 0, "There are no quests for the user.")
    for i in range(0, 3):
      quest_name = "Test Quest %d" % i
      quest = Quest(
          name=quest_name,
          quest_slug="test_quest_%d" % i,
          description=quest_name,
          level=1,
          unlock_conditions="True",
          completion_conditions="False" # User cannot complete these.
      )
      quest.save()
    
    quests = get_quests(self.user)
    self.assertEqual(quests.count(), 3, "User should have 3 quests available.")
    
    # Test that if we add another quest, the user still has the 3 original quests.
    quest = Quest(
        name="Another quest",
        quest_slug="another_quest",
        description="another quest",
        level=1,
        unlock_conditions="True",
        completion_conditions="False",
    )
    quest.save()
    
    quests = get_quests(self.user)
    self.assertEqual(quests.count(), 3, "User should still have 3 quests available.")
    self.assertTrue(quest not in quests, "New quest should not be in quests.")
    
    # Mark a quest as completed so that the new quest is picked up.
    member = QuestMember.objects.filter(user=self.user)[0]
    member.completed = True
    member.save()
    
    quests = get_quests(self.user)
    self.assertEqual(quests.count(), 3, "User should have 3 quests available.")
    self.assertTrue(quest in quests, "New quest should be in quests.")
    
  def testBasicPrerequisites(self):
    """Tests that the user can only get quests for which they meet the prerequisites."""
    quest = Quest(
        name="Test quest",
        quest_slug="test_quest",
        description="test quest",
        level=1,
        unlock_conditions="False",
        completion_conditions="False",
    )
    quest.save()
    
    quests = get_quests(self.user)
    self.assertEqual(quests.count(), 0, "User should not have this quest available.")
    
    quest.unlock_conditions = "True"
    quest.save()
    quests = get_quests(self.user)
    self.assertEqual(quests.count(), 1, "User should now have one quest.")
    
  def testBasicCompletion(self):
    """Tests that the user can complete quests."""
    quest = Quest(
        name="Test quest",
        quest_slug="test_quest",
        description="test quest",
        level=1,
        unlock_conditions="True",
        completion_conditions="False",
    )
    quest.save()
    
    quests = get_quests(self.user)
    self.assertEqual(quests.count(), 1, "User should have one quest.")
    
    possibly_completed_quests(self.user)
    complete_quests = self.user.quest_set.filter(questmember__completed=True)
    self.assertTrue(quest not in complete_quests, "Quest should not be completed.")
    
    quest.completion_conditions = True
    quest.save()
    possibly_completed_quests(self.user)
    complete_quests = self.user.quest_set.filter(questmember__completed=True)
    self.assertTrue(quest in complete_quests, "Quest should be in the user's complete quests list.")
    
class QuestConditionsTest(TestCase):
  """
  Tests for the possible quest conditions.
  """
  def setUp(self):
    self.user = User(username="testuser", password="password")
    self.user.save()
    
    self.quest = Quest(
        name="Test quest",
        quest_slug="test_quest",
        description="test quest",
        level=1,
        unlock_conditions="True",
        completion_conditions="False",
    )
    self.quest.save()
    
  def testActivitiesNumCompleted(self):
    """Test that completing an activity works with num_activities_completed and has_task."""
    activity = Activity(
        type="activity",
        name="Test",
        title="Test activity",
        description="Variable points!",
        duration=10,
        point_value=10,
        pub_date=datetime.datetime.today(),
        expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
        confirm_type="text",
    )
    activity.save()
    
    # Test activities
    member = ActivityMember(user=self.user, activity=activity, approval_status="pending")
    member.save()
    self.assertFalse(num_activities_completed(self.user, 1), "User with pending activity should not have completed a task.")
    
    # Test within context of a quest
    self.quest.unlock_conditions = "num_activities_completed(1)"
    self.quest.save()
    quests = get_quests(self.user)
    self.assertTrue(self.quest not in quests, "User should not be able to participate in this quest.")
    
    member.approval_status = "approved"
    member.save()
    self.assertTrue(num_activities_completed(self.user, 1), "User that has an approved activity did not complete a task.")
    
    # Check that the user can now add the quest.
    quests = get_quests(self.user)
    self.assertTrue(self.quest in quests, "User should be able to participate in this quest.")
    
    # Test as a completion condition.
    self.quest.completion_conditions = "num_activities_completed(2)"
    self.quest.save()
    completed_quests = possibly_completed_quests(self.user)
    self.assertTrue(self.quest not in completed_quests, "User should not be able to complete the quest.")
    
    self.quest.completion_conditions = "num_activities_completed(1)"
    self.quest.save()
    completed_quests = possibly_completed_quests(self.user)
    self.assertTrue(self.quest in completed_quests, "User should have completed the quest.")
    
  def testHasActivity(self):
    """Test that completing an activity works with has_task."""
    activity = Activity(
        type="activity",
        name="Test",
        title="Test activity",
        description="Variable points!",
        duration=10,
        point_value=10,
        pub_date=datetime.datetime.today(),
        expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
        confirm_type="text",
    )
    activity.save()
    
    # Test within context of a quest
    self.quest.unlock_conditions = "has_task('Test')"
    self.quest.save()
    quests = get_quests(self.user)
    self.assertTrue(self.quest not in quests, "User should not be able to participate in this quest.")
    
    member = ActivityMember(user=self.user, activity=activity, approval_status="pending")
    member.save()
    self.assertTrue(has_task(self.user, "Test"), "User should have a pending task.")
    
    quests = get_quests(self.user)
    self.assertTrue(self.quest in quests, "User should be able to participate in this quest.")
    
    member.approval_status = "approved"
    member.save()
    self.assertTrue(has_task(self.user, "Test"), "User should have a completed task.")
    
    # Test as a completion condition.
    self.quest.completion_conditions = "not has_task('Test')"
    self.quest.save()
    completed_quests = possibly_completed_quests(self.user)
    self.assertTrue(self.quest not in completed_quests, "User should not be able to complete the quest.")
    
    self.quest.completion_conditions = "has_task('Test')"
    self.quest.save()
    completed_quests = possibly_completed_quests(self.user)
    self.assertTrue(self.quest in completed_quests, "User should have completed the quest.")
  
  def testCommitmentsNumCompleted(self):
    """Tests that num_activities_completed works for a completed commitment."""
    commitment = Commitment(
        title="Test commitment",
        type="commitment",
        name="Test",
        description="A commitment!",
        point_value=10,
    )
    commitment.save()
    
    member = CommitmentMember(user=self.user, commitment=commitment)
    member.save()
    self.assertFalse(num_activities_completed(self.user, 1), "User with commitment in progress should not have completed a task.")
    
    # Test as an unlock condition
    self.quest.unlock_conditions = "num_activities_completed(1)"
    self.quest.save()
    self.assertTrue(self.quest not in get_quests(self.user), "User should not be able to participate in this quest.")
    
    member.award_date = datetime.datetime.today()
    member.save()
    self.assertTrue(num_activities_completed(self.user, 1), "User that has a completed commitment did not complete a task.")
    self.assertTrue(self.quest in get_quests(self.user), "User should be able to participate in this quest.")
    
    # Test as a completion condition
    self.quest.completion_conditions = "num_activities_completed(2)"
    self.quest.save()
    self.assertTrue(self.quest not in possibly_completed_quests(self.user), "User should not be able to complete this quest.")
    
    self.quest.completion_conditions = "num_activities_completed(1)"
    self.quest.save()
    self.assertTrue(self.quest in possibly_completed_quests(self.user), "User should be able to complete this quest.")
    
  def testHasCommitment(self):
    """Tests that has_task works for a commitment in progress."""
    commitment = Commitment(
        title="Test commitment",
        type="commitment",
        name="Test",
        description="A commitment!",
        point_value=10,
    )
    commitment.save()
    
    # Test as an unlock condition.
    self.quest.unlock_conditions = "has_task('Test')"
    self.quest.save()
    self.assertTrue(self.quest not in get_quests(self.user), "User should not be able to participate in this quest.")
    
    member = CommitmentMember(user=self.user, commitment=commitment)
    member.save()
    self.assertTrue(has_task(self.user, "Test"), "User should have a commitment in progress.")
    self.assertTrue(self.quest in get_quests(self.user), "User should be able to participate in this quest.")
    
    member.award_date = datetime.datetime.today()
    member.save()
    self.assertTrue(has_task(self.user, "Test"), "User should have a completed commitment.")
    
    # Test as a completion condition
    self.quest.completion_conditions = "not has_task('Test')"
    self.quest.save()
    self.assertTrue(self.quest not in possibly_completed_quests(self.user), "User should not be able to complete this quest.")
    
    self.quest.completion_conditions = "has_task('Test')"
    self.quest.save()
    self.assertTrue(self.quest in possibly_completed_quests(self.user), "User should be able to complete this quest.")
    
  def testBadgeAwarded(self):
    """Tests that badge awarded works for a user."""
    from components.makahiki_badges.user_badges import DailyVisitorBadge
    badges.register(DailyVisitorBadge)
    
    profile = self.user.get_profile()
    self.assertFalse(badge_awarded(self.user, "dailyvisitor"), "New user should not be awarded the daily visitor badge.")
    
    # Test as a quest unlock condition.
    self.quest.unlock_conditions = "badge_awarded('dailyvisitor')"
    self.quest.save()
    self.assertTrue(self.quest not in get_quests(self.user), "User should not be able to participate in this quest.")
    
    self.quest.unlock_conditions = "not badge_awarded('dailyvisitor')"
    self.quest.save()
    self.assertTrue(self.quest in get_quests(self.user), "User should be able to participate in this quest.")
    
    self.quest.completion_conditions = "badge_awarded('dailyvisitor')"
    self.quest.save()
    self.assertTrue(self.quest not in possibly_completed_quests(self.user), "User should not be able to complete this quest.")
    
    profile.daily_visit_count = 3
    profile.save()
    badges.possibly_award_badge("dailyvisitor", user=self.user)
    self.assertTrue(badge_awarded(self.user, "dailyvisitor"), "User should have been awarded the daily visitor badge.")
    self.assertTrue(self.quest in possibly_completed_quests(self.user), "User should have completed this quest.")
