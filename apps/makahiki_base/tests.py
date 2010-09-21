import simplejson as json
import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

import competition_settings as settings
from makahiki_base.models import Article
from makahiki_base import get_round_info, get_theme, get_current_round

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
    
    theme = get_theme()
    self.assertEqual(theme, settings.MAKAHIKI_THEME_SETTINGS["default"], "Check that we can retrieve the default theme.")
    
    settings.MAKAHIKI_THEME = "test"
    theme = get_theme()
    self.assertEqual(theme, settings.MAKAHIKI_THEME_SETTINGS["test"], "Check that we can retrieve the test theme.")
    
    settings.MAKAHIKI_THEME = "foo"
    theme = get_theme()
    self.assertEqual(theme, settings.MAKAHIKI_THEME_SETTINGS["default"], "Check that an unknown theme returns the default.")
    
    settings.MAKAHIKI_THEME = None
    theme = get_theme()
    self.assertEqual(theme, settings.MAKAHIKI_THEME_SETTINGS["default"], "Check that no theme returns the default.")
    
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
    
class IndexFunctionalTestCase(TestCase):
  fixtures = ["base_data.json", "user_data.json"]
  
  def testHomepageHeadlines(self):
    """Check that the headline links in the home page are correct."""
    response = self.client.get(reverse("home"))
    articles = Article.objects.all()
    for article in articles:
      article_url = reverse("view_article", args=(article.slug,))
      message = "Checking that link to '%s' appears in headline and listing."
      self.assertContains(response, article_url, count=2, msg_prefix=message)
      
    # Test using a new article.
    article = Article(title="Test Article", abstract="This is a test", content="Testing testing.")
    article.save()
    article_url = reverse("view_article", args=(article.slug,))
    response = self.client.get(reverse("home"))
    self.assertContains(response, article_url, count=2, msg_prefix="Checking that a new test article appears.")
    
  def testHomepageRedirect(self):
    """Tests that a logged in user goes to their profile page."""
    
    response = self.client.get(reverse("index"))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "homepage.html", 
          "Check that the home page template is used for non-authenticated users.")
    
    user = User.objects.get(username="user")
    self.client.post('/account/login/', {"username": user.username, "password": "changeme", "remember": False})
    response = self.client.get(reverse("index"), follow=True)
    self.assertTemplateUsed(response, "makahiki_profiles/profile.html", "Check that the user is taken to their profile.")
    response = self.client.get(reverse("home"))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "homepage.html", 
          "Check that the home page is still accessible in the tab.")
          
  def testJsonConfiguration(self):
    """Tests that JSON configuration is stored within multiple pages for widgets."""
    
    round_json = json.dumps(get_round_info())
    theme_json = json.dumps(get_theme())
    
    response = self.client.get(reverse("index"))
    self.assertContains(response, round_json, msg_prefix="Check that the round info is inserted in the index.")
    self.assertContains(response, theme_json, msg_prefix="Check that the theme info is inserted in the index.")
    
    user = User.objects.get(username="user")
    self.client.post('/account/login/', {"username": user.username, "password": "changeme", "remember": False})
    response = self.client.get(reverse("profile_detail", args=(user.pk,)))
    self.assertContains(response, round_json, msg_prefix="Check that the round info is inserted in the user page.")
    self.assertContains(response, theme_json, msg_prefix="Check that the theme info is inserted in the user page.")
    