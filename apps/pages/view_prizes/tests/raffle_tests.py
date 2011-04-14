import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings

from components.floors.models import Floor
from components.prizes.models import RafflePrize, RaffleDeadline
    
class RafflePrizesTestCase(TestCase):
  fixtures = ["base_floors.json"]

  def setUp(self):
    """Set up rounds, floor, and a user."""
    # Set up rounds.
    self.saved_rounds = settings.COMPETITION_ROUNDS
    self.saved_start = settings.COMPETITION_START
    self.saved_end = settings.COMPETITION_END
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

    # Set up user
    self.user = User.objects.create_user("user", "user@test.com", password="changeme")
    floor = Floor.objects.all()[0]
    profile = self.user.get_profile()
    profile.floor = floor
    profile.setup_complete = True
    profile.setup_profile = True
    profile.save()

    self.client.login(username="user", password="changeme")

    # Set up raffle deadline
    self.deadline = RaffleDeadline(
        round_name="Round 2", 
        pub_date=datetime.datetime.today() - datetime.timedelta(hours=1),
        end_date=datetime.datetime.today() + datetime.timedelta(days=5),
    )
    self.deadline.save()

  def testIndex(self):
    """Check that we can load the index page."""
    response = self.client.get(reverse("prizes_index"))
    self.failUnlessEqual(response.status_code, 200)
    self.assertContains(response, "Round 2 Raffle", msg_prefix="We should be in round 2 of the raffle.")
    self.assertContains(response, "Your total raffle tickets: 0 Allocated right now: 0 Available: 0",
        msg_prefix="User should not have any raffle tickets.")
    date_string = self.deadline.end_date.strftime("%A, %B %d, %Y, ")
    # Workaround since strftime doesn't remove the leading 0 in hours.
    hour = self.deadline.end_date.hour
    if hour == 0:
      hour = hour + 12
    elif hour > 12:
      hour = hour - 12
    date_string = date_string + str(hour) + self.deadline.end_date.strftime("%p")
    self.assertContains(response, "Deadline for Round 2 submissions: " + date_string, 
        msg_prefix="Raffle should have the correct deadline.")

  def tearDown(self):
    """
    Restores saved settings.
    """
    # Restore rounds.
    settings.COMPETITION_ROUNDS = self.saved_rounds
    settings.COMPETITION_START = self.saved_start
    settings.COMPETITION_END = self.saved_end