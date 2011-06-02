from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from components.floors.models import Floor
from components.help_topics.models import HelpTopic

class HelpFunctionalTestCase(TestCase):
  fixtures = ["base_floors.json"]
  
  def setUp(self):
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
    response = self.client.get(reverse("help_index"))
    self.failUnlessEqual(response.status_code, 200)
  
  def testTopic(self):
    """Check that we can view a help topic."""
    topic = HelpTopic(
        title="A topic",
        slug="a-topic",
        category="rules",
        contents="This is a topic",
    )
    topic.save()
    
    response = self.client.get(reverse("help_index"))
    self.assertContains(response, topic.title, msg_prefix="Page should have topic listed.")
    response = self.client.get(reverse("help_topic", args=(topic.category, topic.slug)))
    self.failUnlessEqual(response.status_code, 200)
    self.assertContains(response, topic.contents)
