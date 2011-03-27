import simplejson as json
import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings

from components.makahiki_base.models import Article
from components.makahiki_base import get_round_info, get_theme, get_current_round
from components.makahiki_base.templatetags.class_tags import insert_classes, get_id_and_classes
from css_rules import default

class BaseUnitTestCase(TestCase):
  def testThemeRetrieval(self):
    """Checks that the correct theme is retrieved based on the settings."""
    
    # Store settings for later.
    saved_theme = settings.MAKAHIKI_THEME
    saved_theme_settings = settings.MAKAHIKI_THEME_SETTINGS
    
    # Create test settings.
    settings.MAKAHIKI_THEME = "default"
    settings.MAKAHIKI_THEME_SETTINGS = {
      "default" : {
        "widgetBackgroundColor" : '#F5F3E5',
        "widgetHeaderColor" : '#459E00',
        "widgetHeaderTextColor" : 'white',
        "widgetTextColor" : '#312E25',
        "widgetTextFont" : 'Ariel, sans serif',
        "windowNavBarColor" : '#2F6B00',
      },
      "test" : {
        "widgetBackgroundColor" : 'white',
        "widgetHeaderColor" : 'black',
        "widgetHeaderTextColor" : 'white',
        "widgetTextColor" : 'black',
        "widgetTextFont" : 'Ariel, sans serif',
        "windowNavBarColor" : 'green',
      },
    }
    
    theme, contents = get_theme()
    self.assertEqual(contents, settings.MAKAHIKI_THEME_SETTINGS["default"], "Check that we can retrieve the default theme.")
    
    settings.MAKAHIKI_THEME = "test"
    theme, contents = get_theme()
    self.assertEqual(contents, settings.MAKAHIKI_THEME_SETTINGS["test"], "Check that we can retrieve the test theme.")
    
    settings.MAKAHIKI_THEME = "foo"
    theme, contents = get_theme()
    self.assertEqual(contents, settings.MAKAHIKI_THEME_SETTINGS["default"], "Check that an unknown theme returns the default.")
    
    settings.MAKAHIKI_THEME = None
    theme, contents = get_theme()
    self.assertEqual(contents, settings.MAKAHIKI_THEME_SETTINGS["default"], "Check that no theme returns the default.")
    
    # Restore settings
    settings.MAKAHIKI_THEME = saved_theme
    settings.MAKAHIKI_THEME_SETTINGS = saved_theme_settings
    
  def testCurrentRound(self):
    """Tests that the current round retrieval is correct."""
    saved_rounds = settings.COMPETITION_ROUNDS
    current_round = "Round 1"
    start = datetime.date.today() - datetime.timedelta(days=3)
    end = start + datetime.timedelta(days=7)
    
    settings.COMPETITION_ROUNDS = {
      "Round 1" : {
        "start": start.strftime("%Y-%m-%d"),
        "end": end.strftime("%Y-%m-%d"),
      },
    }
    
    round_info = get_current_round()
    self.assertEqual(round_info["title"], current_round, "Test that the current round is returned.")
    
    start = datetime.date.today() - datetime.timedelta(days=14)
    end = start + datetime.timedelta(days=7)
    
    settings.COMPETITION_ROUNDS = {
      "Round 1" : {
        "start": start.strftime("%Y-%m-%d"),
        "end": end.strftime("%Y-%m-%d"),
      },
    }
    
    round_info = get_current_round()
    self.assertTrue(round_info is None, "Test that there is no current round.")
    
    # Restore settings.
    settings.COMPETITION_ROUNDS = saved_rounds
    
class ClassTagsUnitTests(TestCase):
  def setUp(self):
    """Stores the current values of the CSS keys so that we can modify them."""
    self.saved_classes = default.CSS_CLASSES
    self.saved_ids = default.CSS_IDS
    default.CSS_CLASSES = {"foo": "bar"}
    default.CSS_IDS = {"foo_id": "bar_id"}
    
  """Tests the ability to insert class tags."""
  def testDefaultClassRetrieval(self):
    """Checks that default values can be retrieved."""
    class_name = default.CSS_CLASSES.keys()[0]
    self.assertEqual(insert_classes(class_name), default.CSS_CLASSES[class_name], 
                    "Check that insert classes returns the correct value from the dictionary.")
                    
  def testEmptyClassRetrieval(self):
    """Checks that disabling RETURN_CLASSES returns empty strings for classes."""
    saved_setting = default.RETURN_CLASSES
    default.RETURN_CLASSES = False
    class_name = default.CSS_CLASSES.keys()[0]
    self.assertEqual(insert_classes(class_name), "", 
                    "Check that insert classes now returns an empty string.")
                    
    # Restore setting
    default.RETURN_CLASSES = saved_setting
    
  def testIdAndClassExpansion(self):
    """Tests the ability to expand an id into an id and classes."""
    tag_id = default.CSS_IDS.keys()[0]
    expected_string = 'id="%s" class="%s"' % (tag_id, default.CSS_IDS[tag_id])
    self.assertEqual(get_id_and_classes(tag_id), expected_string, 
                    "Expected: %s but got %s." % (expected_string, get_id_and_classes(tag_id)))
                    
  def testDisabledIdExpansion(self):
    """Tests the ability to expand an id into an id and classes."""
    saved_setting = default.RETURN_CLASSES
    default.RETURN_CLASSES = False
    
    tag_id = default.CSS_IDS.keys()[0]
    expected_string = 'id="%s"' % (tag_id,)
    self.assertEqual(get_id_and_classes(tag_id), expected_string, 
                    "Expected: %s but got %s." % (expected_string, get_id_and_classes(tag_id)))
                    
    # Restore setting
    default.RETURN_CLASSES = saved_setting
  def tearDown(self):
    default.CSS_CLASSES = self.saved_classes
    default.CSS_IDS = self.saved_ids
    