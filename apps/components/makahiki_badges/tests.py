from django.test import TestCase
from django.contrib.auth.models import User

from lib.brabeion import badges

from components.makahiki_badges.user_badges import DailyVisitorBadge

badges.register(DailyVisitorBadge)

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