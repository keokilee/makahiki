from django.test import TestCase
from django.contrib.auth.models import User

from components.makahiki_profiles.models import Profile

class DailyVisitorBadgeTest(TestCase):
  def test_awarding(self):
    """
    Tests that the daily visitor badge is awarded to a user.
    """
    user = User(username="testuser", password="password")
    
    self.assertEqual(user.badges_awarded, [], "Check that no badges are awarded.")


