import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from lib.brabeion import badges

from components.makahiki_badges import user_badges
from components.activities.models import Commitment, CommitmentMember
from components.makahiki_badges.management.commands.award_badge import award_badge

class DailyVisitorBadgeTest(TestCase):
  def test_awarding(self):
    """
    Tests that the daily visitor badge is awarded to a user.
    """
    user = User(username="testuser", password="password")
    user.save()
    
    self.assertEqual(user.badges_earned.count(), 0, "Check that no badges are awarded.")
    profile = user.get_profile()
    profile.daily_visit_count = 1
    profile.save()
    badges.possibly_award_badge("dailyvisitor", user=user)
    
    self.assertEqual(user.badges_earned.count(), 0, "Check that still no badges are awarded.")
    
    profile.daily_visit_count = 3
    profile.save()
    badges.possibly_award_badge("dailyvisitor", user=user)
    
    self.assertEqual(user.badges_earned.count(), 1, "Check that a badge has been awarded.")
    self.assertEqual(user.badges_earned.all()[0].slug, "dailyvisitor", "Check that the daily visitor badge was awarded.")
    
class FullyCommittedBadgeTest(TestCase):
  def test_awarding(self):
    """
    Tests that the fully committed badge is awarded to a user.
    """
    user = User(username="testuser", password="password")
    user.save()
    
    commitments = []
    # Create 5 test commitments.
    for i in range(0, 5):
      commitment = Commitment(
          title="Test commitment %i" % i,
          description="A commitment!",
          point_value=10,
      )
      commitment.save()
      commitments.append(commitment)
    
    # Add the commitments one by one and see if the user earned a badge.
    # The badge should not be awarded until the very end.
    for index, commitment in enumerate(commitments):
      self.assertEqual(user.badges_earned.count(), 0, "Badge should not be awarded after %i commitments" % index)
      member = CommitmentMember(user=user, commitment=commitment, award_date=datetime.datetime.today())
      member.save()
      self.assertEqual(user.badges_earned.count(), 0, "Badge should not be awarded after commitment %i is awarded" % index)
      member.award_date = None
      member.save()
      
    self.assertEqual(user.badges_earned.count(), 1, "A badge should have been awarded.")
    self.assertEqual(user.badges_earned.all()[0].slug, "fully_committed", "Check that the Fully Committed badge was awarded.")
    
class ManagementCommandTest(TestCase):
  def test_bug_hunter_award(self):
    """
    Test that we can award the bug hunter badge.
    """
    user = User.objects.create_user("testuser", "user@test.com")
    award_badge(user_badges.BugHunterBadge.slug, user)
    self.assertEqual(user.badges_earned.count(), 1, "Badge should have been awarded.")
      