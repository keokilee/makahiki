from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from components.floors.models import Floor, Post
from pages.news import DEFAULT_POST_COUNT

class NewsFunctionalTestCase(TestCase):
  fixtures = ["base_floors.json"]
  
  def testIndex(self):
    """Check that we can load the index page."""
    user = User.objects.create_user("user", "user@test.com", password="changeme")
    floor = Floor.objects.all()[0]
    profile = user.get_profile()
    profile.floor = floor
    profile.setup_complete = True
    profile.profile_setup = True
    profile.save()
    
    self.client.login(username="user", password="changeme")
    
    response = self.client.get(reverse("news_index"))
    self.failUnlessEqual(response.status_code, 200)
    
  def testAjaxPosts(self):
    """Test that we can load new posts via AJAX."""
    user = User.objects.create_user("user", "user@test.com", password="changeme")
    floor = Floor.objects.all()[0]
    profile = user.get_profile()
    profile.floor = floor
    profile.setup_complete = True
    profile.profile_setup = True
    profile.save()
    
    self.client.login(username="user", password="changeme")
    
    # Generate test posts.
    for i in range(0, DEFAULT_POST_COUNT + 1):
      text = "Testing AJAX response %d." % i
      post = Post(user=user, floor=floor, text=text)
      post.save()
    
    second_post = Post.objects.all().order_by("-pk")[0]
    response = self.client.get(reverse("news_more_posts"), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    self.failUnlessEqual(response.status_code, 200)
    self.assertNotContains(response, "Testing AJAX response 0.")
    for i in range(1, DEFAULT_POST_COUNT + 1):
      self.assertContains(response, "Testing AJAX response %d" % i)
    
    response = self.client.get(reverse("news_more_posts") + ("?last_post=%d" % second_post.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    self.assertContains(response, "Testing AJAX response 0.", 1)
      
      
      
    
    