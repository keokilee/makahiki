import simplejson as json
import datetime

from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse

class RoundApiFunctionalTest(TestCase):
  """
  Tests the API through the Django test client.
  """
  
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
    
  def testJsonResponse(self):
    """Test that we get the correct JSON API response."""
    
    response = self.client.get(reverse('api_rounds'))
    self.failUnlessEqual(response.status_code, 200)
    self.assertEqual(response["Content-Type"], "application/json")
    
    # Check that the content is correct.
    json_content = json.loads(response.content)
    
    self.assertTrue(json_content.has_key("start"), "Check that the competition start date is included.")
    self.assertTrue(json_content.has_key("end"), "Check that the competition end date is included.")
    self.assertTrue(json_content.has_key("Round 1"), "Check that Round 1 is included.")
    self.assertEqual(len(json_content), 3, "Check that these are the only 3 items.")
    
  def tearDown(self):
    settings.COMPETITION_ROUNDS = self.saved_rounds
    settings.COMPETITION_START = self.saved_start
    settings.COMPETITION_END = self.saved_end


