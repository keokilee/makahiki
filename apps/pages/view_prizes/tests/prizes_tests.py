import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings

from components.floors.models import Floor
from components.prizes.models import Prize

class PrizesFunctionalTestCase(TestCase):
  fixtures = ["base_floors.json", "test_prizes.json"]
  
  def setUp(self):
    """Set up a floor and log in."""
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
    response = self.client.get(reverse("prizes_index"))
    self.failUnlessEqual(response.status_code, 200)
    
    for prize in Prize.objects.all():
      self.assertContains(response, prize.title, msg_prefix="Prize not found on prize page")
      
  def testLeadersInRound1(self):
    """Test that the leaders are displayed correctly in round 1."""
    saved_rounds = settings.COMPETITION_ROUNDS
    saved_start = settings.COMPETITION_START
    saved_end = settings.COMPETITION_END
    start = datetime.date.today()
    end1 = start + datetime.timedelta(days=7)
    end2 = start + datetime.timedelta(days=14)
    
    settings.COMPETITION_ROUNDS = {
      "Round 1" : {
        "start": start.strftime("%Y-%m-%d"),
        "end": end1.strftime("%Y-%m-%d"),
      },
      "Round 2" : {
        "start": end1.strftime("%Y-%m-%d"),
        "end": end2.strftime("%Y-%m-%d"),
      },
    }
    settings.COMPETITION_START = start.strftime("%Y-%m-%d")
    settings.COMPETITION_END = end2.strftime("%Y-%m-%d")
    
    profile =  self.user.get_profile()
    profile.name = "Test User"
    profile.add_points(10, datetime.datetime.today(), "test")
    floor = profile.floor
    profile.save()
    
    response = self.client.get(reverse("prizes_index"))
    self.assertContains(response, "Current leader: " + str(profile), count=2,
        msg_prefix="Individual prizes should have user as the leader.")
    self.assertContains(response, "Current leader: " + str(floor), count=2,
        msg_prefix="Floor points prizes should have floor as the leader")
    self.assertContains(response, "Current leader: <span id='round-1-leader'></span>", count=1,
        msg_prefix="Span for round 1 energy prize should be inserted.")
    self.assertNotContains(response, "Current leader: <span id='round-2-leader'></span>",
        msg_prefix="Span for round 2 energy prize should not be inserted.")
    self.assertContains(response, "Current leader: <span id='overall-leader'></span>", count=1,
        msg_prefix="Span for round 1 energy prize should be inserted.")
    self.assertContains(response, "Current leader: TBD", count=3,
        msg_prefix="Round 2 prizes should not have a leader yet.")
        
    # Restore rounds.
    settings.COMPETITION_ROUNDS = saved_rounds
    settings.COMPETITION_START = saved_start
    settings.COMPETITION_END = saved_end
    
  def testLeadersInRound2(self):
    """Test that the leaders are displayed correctly in round 2."""
    saved_rounds = settings.COMPETITION_ROUNDS
    saved_start = settings.COMPETITION_START
    saved_end = settings.COMPETITION_END
    start = datetime.date.today() - datetime.timedelta(days=8)
    end1 = start + datetime.timedelta(days=7)
    end2 = start + datetime.timedelta(days=14)

    settings.COMPETITION_ROUNDS = {
      "Round 1" : {
        "start": start.strftime("%Y-%m-%d"),
        "end": end1.strftime("%Y-%m-%d"),
      },
      "Round 2" : {
        "start": end1.strftime("%Y-%m-%d"),
        "end": end2.strftime("%Y-%m-%d"),
      },
    }
    settings.COMPETITION_START = start.strftime("%Y-%m-%d")
    settings.COMPETITION_END = end2.strftime("%Y-%m-%d")
    
    profile =  self.user.get_profile()
    profile.add_points(10, datetime.datetime.today(), "test")
    profile.name = "Test User"
    floor = profile.floor
    profile.save()

    response = self.client.get(reverse("prizes_index"))
    self.assertContains(response, "Winner: ", count=3,
        msg_prefix="There should be winners for three prizes.")
    self.assertContains(response, "Current leader: " + str(profile), count=2,
        msg_prefix="Individual prizes should have user as the leader.")
    self.assertContains(response, "Current leader: <span id='round-2-leader'></span>", count=1,
        msg_prefix="Span for round 2 energy prize should be inserted.")
    self.assertContains(response, "Current leader: " + str(floor), count=2,
        msg_prefix="Floor points prizes should have floor as the leader")

    # Restore rounds.
    settings.COMPETITION_ROUNDS = saved_rounds
    settings.COMPETITION_START = saved_start
    settings.COMPETITION_END = saved_end
