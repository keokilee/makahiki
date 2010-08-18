import simplejson as json
import datetime

from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse

import competition_settings
from makahiki_profiles.models import Profile
from floors.models import Floor
from floors.models import Dorm
from standings import MAX_INDIVIDUAL_STANDINGS

class JsonApiFunctionalTestCase(TestCase):
  """
  Tests accessing the API through the Django test client.
  """
  
  fixtures = ["base_data.json", "user_data.json"]
  
  def setUp(self):
    """Set the competition settings to the current date for testing."""
    self.saved_rounds = settings.COMPETITION_ROUNDS
    self.saved_start = settings.COMPETITION_START
    self.saved_end = settings.COMPETITION_END
    start = datetime.date.today()
    end = start + datetime.timedelta(days=7)
    
    settings.COMPETITION_ROUNDS = {
      "Round 1" : {
        "start": start.strftime("%Y-%m-%d"),
        "end": end.strftime("%Y-%m-%d"),
      },
    }
    
    settings.COMPETITION_START = start.strftime("%Y-%m-%d")
    settings.COMPETITION_END = end.strftime("%Y-%m-%d")
    
    if competition_settings.COMPETITION_GROUP_NAME:
      self.floor_label = competition_settings.COMPETITION_GROUP_NAME
    else:
      self.floor_label = "Floor"
    
  def testRoundResponse(self):
    """Test that we get the correct JSON API response when accessing rounds."""
    
    response = self.client.get(reverse("api_rounds"))
    self.failUnlessEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], "application/json")
    
    # Check that the content is correct.
    json_content = json.loads(response.content)
    
    self.assertTrue(json_content.has_key("start"), "Check that the competition start date is included.")
    self.assertTrue(json_content.has_key("end"), "Check that the competition end date is included.")
    self.assertTrue(json_content.has_key("Round 1"), "Check that Round 1 is included.")
    self.assertEqual(len(json_content), 3, "Check that these are the only 3 items.")
    
  def testFloorStandingsResponse(self):
    """Test that we get the correct JSON API response when accessing floor standings."""

    response = self.client.get(reverse("api_standings", args=("floor",)))
    self.assertContains(response, "Round 1")
    self.assertContains(response, "Overall")
    self.assertEqual(response["Content-Type"], "application/json")
    
    json_content = json.loads(response.content)
    self.assertEqual(len(json_content[0]["info"]), Floor.objects.count())
    self.assertEqual(len(json_content[1]["info"]), Floor.objects.count())
    
  def testIndividualStandingsResponse(self):
    """Test that we get the correct JSON API response when accessing individual standings."""
    
    response = self.client.get(reverse("api_standings", args=("individual",)))
    self.assertContains(response, "Round 1")
    self.assertContains(response, "Overall")
    self.assertEqual(response["Content-Type"], "application/json")
    
    json_content = json.loads(response.content)
    self.assertEqual(len(json_content[0]["info"]), MAX_INDIVIDUAL_STANDINGS)
    self.assertEqual(len(json_content[1]["info"]), MAX_INDIVIDUAL_STANDINGS)
    
  def testStandingsWithDormResponse(self):
    """Test that we get the correct JSON API response when requesting information for a dorm."""
    
    dorm = Dorm.objects.all()[0]
    
    url = reverse("api_standings", args=("floor",))
    url += "?dorm=" + dorm.name
    response = self.client.get(url)
    
    self.assertContains(response, "Round 1")
    self.assertContains(response, "Overall")
    self.assertEqual(response["Content-Type"], "application/json")
    
    json_content = json.loads(response.content)
    self.assertEqual(len(json_content[0]["info"]), Floor.objects.filter(dorm=dorm).count())
    self.assertEqual(len(json_content[1]["info"]), Floor.objects.filter(dorm=dorm).count())
    
    
  def tearDown(self):
    settings.COMPETITION_ROUNDS = self.saved_rounds
    settings.COMPETITION_START = self.saved_start
    settings.COMPETITION_END = self.saved_end


