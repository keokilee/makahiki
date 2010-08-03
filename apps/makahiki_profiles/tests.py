import datetime

from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from activities.models import Activity, ActivityMember
from makahiki_profiles.models import Profile, ScoreboardEntry
    
class ProfileUnitTests(TestCase):
  fixtures = ["base_data.json", "user_data.json"]
  
  def setUp(self):
    """Set the competition settings to the current date for testing."""
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
    user = User.objects.all()[0]
    entry, created = ScoreboardEntry.objects.get_or_create(
                        profile=user.get_profile(), 
                        round_name=self.current_round,
                      )
    round_points = entry.points

    activity = Activity.objects.all()[0]
    activity_points = activity.point_value

    activity_member = ActivityMember(user=user, activity=activity)
    activity_member.approval_status = "approved"
    activity_member.save()
    
    # Verify that the points for the round has been updated.
    entry, created = ScoreboardEntry.objects.get_or_create(
                        profile=user.get_profile(), 
                        round_name=self.current_round,
                      )
                    
    self.assertFalse(created)
    current_score = entry.points
    self.assertEqual(round_points + activity_points, current_score)
    
  def tearDown(self):
    """Restore the saved settings."""
    settings.COMPETITION_ROUNDS = self.saved_rounds
    