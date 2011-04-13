import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from lib.brabeion import badges

from components.activities.models import Activity, ActivityMember, Commitment, CommitmentMember
from components.quests import get_quests, has_task, num_activities_completed, badge_awarded, possibly_completed_quests
from components.quests.models import Quest, QuestMember
from components.quests.admin import QuestAdminForm

class QuestTest(TestCase):
  def setUp(self):
    self.user = User(username="testuser", password="password")
    self.user.save()
    
  def testGetQuests(self):
    """Tests that we can get the quests for a user."""
    # Create some sample quests.
    self.assertEqual(len(get_quests(self.user)["available_quests"]), 0, "There are no quests for the user.")
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
    self.assertEqual(len(quests["available_quests"]), 3, "User should have 3 quests available.")
    
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
    self.assertEqual(len(quests["available_quests"]), 3, "User should still have 3 quests available.")
    self.assertTrue(quest not in quests, "New quest should not be in quests.")
    
    # Mark a quest as completed so that the new quest is picked up.
    quests["available_quests"][0].accept(self.user)
    member = QuestMember.objects.filter(user=self.user)[0]
    member.completed = True
    member.save()
    
    quests = get_quests(self.user)
    self.assertEqual(len(quests["available_quests"]), 3, "User should have 3 quests available.")
    self.assertTrue(quest in quests["available_quests"], "New quest should be in quests.")
    
  def testOptOut(self):
    """Test that once a user opts out of a quest, it doesn't show up."""
    quest = Quest(
        name="Another quest",
        quest_slug="another_quest",
        description="another quest",
        level=1,
        unlock_conditions="False", # User cannot unlock this quest
        completion_conditions="False",
    )
    quest.save()
    
    self.assertFalse(quest.opt_out(self.user), "User should not be able to see this quest.")
    
    quest.unlock_conditions = "True"
    quest.save()
    self.assertTrue(quest.opt_out(self.user), "User should be able to opt out of this quest.")
    
    quests = get_quests(self.user)
    self.assertTrue(quest not in quests["available_quests"], "User should not see the quest as available.")
    self.assertTrue(quest not in quests["user_quests"], "User should not have this listed as their current quest.")
    
  def testAccept(self):
    """Test that the user can accept quests."""
    quest = Quest(
        name="Another quest",
        quest_slug="another_quest",
        description="another quest",
        level=1,
        unlock_conditions="False", # User cannot unlock this quest
        completion_conditions="False",
    )
    quest.save()
    
    self.assertFalse(quest.accept(self.user), "User should not be able to accept this quest.")
    self.assertEqual(self.user.quest_set.count(), 0, "User should not have any quests.")
    
    quest.unlock_conditions = "True"
    quest.save()
    self.assertTrue(quest.accept(self.user), "User should be able to accept this quest.")
    self.assertEqual(self.user.quest_set.count(), 1, "User should have an accepted quest.")
    
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
    self.assertEqual(len(quests["available_quests"]), 0, "User should not have this quest available.")
    
    quest.unlock_conditions = "True"
    quest.save()
    quests = get_quests(self.user)
    self.assertEqual(len(quests["available_quests"]), 1, "User should now have one quest.")
    
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
    self.assertEqual(len(quests["available_quests"]), 1, "User should have one quest.")
    
    quests["available_quests"][0].accept(self.user)
    
    possibly_completed_quests(self.user)
    complete_quests = self.user.quest_set.filter(questmember__completed=True)
    self.assertTrue(quest not in complete_quests, "Quest should not be completed.")
    
    quest.completion_conditions = True
    quest.save()
    possibly_completed_quests(self.user)
    complete_quests = self.user.quest_set.filter(questmember__completed=True)
    self.assertTrue(quest in complete_quests, "Quest should be in the user's complete quests list.")
    
    quests = get_quests(self.user)
    self.assertTrue(quest not in quests["available_quests"], "Quest should not be available after completion.")
    self.assertTrue(quest not in quests["user_quests"], "Quest should not be in the user's active quests.")
    
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
    self.assertTrue(self.quest in quests["available_quests"], "User should be able to participate in this quest.")
    
    # Test as a completion condition.
    self.quest.accept(self.user)
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
    self.assertTrue(self.quest in quests["available_quests"], "User should be able to participate in this quest.")
    
    member.approval_status = "approved"
    member.save()
    self.assertTrue(has_task(self.user, "Test"), "User should have a completed task.")
    
    # Test as a completion condition.
    self.quest.accept(self.user)
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
    self.assertTrue(self.quest in get_quests(self.user)["available_quests"], "User should be able to participate in this quest.")
    
    # Test as a completion condition
    self.quest.accept(self.user)
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
    self.assertTrue(self.quest in get_quests(self.user)["available_quests"], "User should be able to participate in this quest.")
    
    member.award_date = datetime.datetime.today()
    member.save()
    self.assertTrue(has_task(self.user, "Test"), "User should have a completed commitment.")
    
    # Test as a completion condition
    self.quest.accept(self.user)
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
    self.assertTrue(self.quest in get_quests(self.user)["available_quests"], "User should be able to participate in this quest.")
    
    self.quest.accept(self.user)
    self.quest.completion_conditions = "badge_awarded('dailyvisitor')"
    self.quest.save()
    self.assertTrue(self.quest not in possibly_completed_quests(self.user), "User should not be able to complete this quest.")
    
    profile.daily_visit_count = 3
    profile.save()
    badges.possibly_award_badge("dailyvisitor", user=self.user)
    self.assertTrue(badge_awarded(self.user, "dailyvisitor"), "User should have been awarded the daily visitor badge.")
    self.assertTrue(self.quest in possibly_completed_quests(self.user), "User should have completed this quest.")

class QuestFunctionalTestCase(TestCase):
  def setUp(self):
    self.user = User.objects.create_user("user", "user@test.com", password="changeme")
    profile = self.user.get_profile()
    profile.setup_profile = True
    profile.setup_complete = True
    profile.save()
    self.client.login(username="user", password="changeme")
    
  def testNoQuests(self):
    """Test that the appropriate text is displayed when there are no quests."""
    response = self.client.get(reverse("home_index"))
    self.assertContains(response, "There are no quests available at this time.  Please check back later!")
    
  def testGetQuests(self):
    """Test that quests show up in the interface."""
    quest = Quest(
        name="Test quest",
        quest_slug="test_quest",
        description="test quest",
        level=1,
        unlock_conditions="False",
        completion_conditions="False",
    )
    quest.save()
    
    response = self.client.get(reverse("home_index"))
    self.failUnlessEqual(response.status_code, 200)
    self.assertNotContains(response, "Test quest", msg_prefix="Test quest should not be available to the user.")
    
    quest.unlock_conditions = "True"
    quest.save()
    response = self.client.get(reverse("home_index"))
    self.assertContains(response, "Test quest", msg_prefix="Test quest should be available to the user.")
    
  def testAcceptQuest(self):
    """Test that a user can accept a quest using a url."""
    quest = Quest(
        name="Test quest",
        quest_slug="test_quest",
        description="test quest",
        level=1,
        unlock_conditions="True",
        completion_conditions="False",
    )
    quest.save()
    
    response = self.client.get(reverse("home_index"))
    self.assertContains(response, "Test quest", msg_prefix="Test quest should be available to the user.")
    response = self.client.post(
        reverse("quests_accept", args=(quest.id,)), 
        follow=True,
        HTTP_REFERER=reverse("home_index"),
    )
    self.assertRedirects(response, reverse("home_index"))
    quests = get_quests(self.user)
    self.assertEqual(len(quests["user_quests"]), 1, "User should have one quest.")
    
  def testOptOutOfQuest(self):
    """Test that a user can opt out of the quest."""
    quest = Quest(
        name="Test quest",
        quest_slug="test_quest",
        description="test quest",
        level=1,
        unlock_conditions="True",
        completion_conditions="True",
    )
    quest.save()
    
    response = self.client.get(reverse("home_index"))
    self.assertContains(response, "Test quest", msg_prefix="Test quest should be available to the user.")
    response = self.client.post(
        reverse("quests_opt_out", args=(quest.id,)), 
        follow=True,
        HTTP_REFERER=reverse("home_index"),
    )
    self.assertRedirects(response, reverse("home_index"))
    self.assertNotContains(response, "Test quest", msg_prefix="Test quest should not be shown.")
    self.assertFalse(response.context["QUESTS"].has_key("completed"), "There should not be any completed quests.")
    
  def testQuestCompletion(self):
    """Test that a user gets a dialog box when they complete a quest."""
    quest = Quest(
        name="Test quest",
        quest_slug="test_quest",
        description="test quest",
        level=1,
        unlock_conditions="True",
        completion_conditions="True",
    )
    quest.save()
    
    response = self.client.get(reverse("home_index"))
    self.assertEqual(len(response.context["QUESTS"]["completed_quests"]), 0, "User should not have any completed quests.")
    
    response = self.client.post(
        reverse("quests_accept", args=(quest.id,)), 
        follow=True,
        HTTP_REFERER=reverse("home_index"),
    )
    self.assertRedirects(response, reverse("home_index"))
    self.assertEqual(len(response.context["QUESTS"]["completed_quests"]), 1, "User should have one completed quest.")
    self.assertTrue(quest in response.context["QUESTS"]["completed_quests"], "Quest should be completed.")
    self.assertTrue(quest not in response.context["QUESTS"]["user_quests"], "Quest should not be loaded as a user quest.")
    self.assertContains(response, "Great job!  You completed the following quest(s):", msg_prefix="Quest complete dialog should appear.")
    
    