import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from components.quests.models import Quest, QuestMember
from components.quests import get_quests, possibly_completed_quests

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