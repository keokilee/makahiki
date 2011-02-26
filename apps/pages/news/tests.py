from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from components.activities.models import Commitment, CommitmentMember
from components.floors.models import Floor, Post
from pages.news import DEFAULT_POST_COUNT

class NewsFunctionalTestCase(TestCase):
  fixtures = ["base_floors.json"]
  def setUp(self):
    self.user = User.objects.create_user("user", "user@test.com", password="changeme")
    self.floor = Floor.objects.all()[0]
    profile = self.user.get_profile()
    profile.floor = self.floor
    profile.setup_complete = True
    profile.setup_profile = True
    profile.save()
    
    self.client.login(username="user", password="changeme")
  
  def testIndex(self):
    """Check that we can load the index page."""
    # Create a commitment that will appear on the news page.
    commitment = Commitment(
                title="Test commitment",
                description="A commitment!",
                point_value=10,
    )
    commitment.save()
    
    member = CommitmentMember(commitment=commitment, user=self.user)
    member.save()
    
    response = self.client.get(reverse("news_index"))
    self.failUnlessEqual(response.status_code, 200)
    self.assertContains(response, commitment.title, 2)
    
  def testPost(self):
    """Test that we can add new post via AJAX."""
    # Test posting an empty post.
    posts = Post.objects.filter(floor=self.floor)
    count = posts.count()
    response = self.client.post(reverse("news_post"), {"post": ""},
        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    self.assertContains(response, "This should not be blank.")
    self.assertEqual(count, posts.count(), "Check that the number of posts did not change.")
    
    post = "Test post via AJAX"
    response = self.client.post(reverse("news_post"), {"post": post}, 
        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    self.failUnlessEqual(response.status_code, 200)
    self.assertContains(response, "Test post via AJAX")
    
    # Check that the new post is in the news feed.
    response = self.client.get(reverse("news_index"))
    self.assertContains(response, post)
    
  def testAjaxPosts(self):
    """Test that we can load new posts via AJAX."""
    # Generate test posts.
    for i in range(0, DEFAULT_POST_COUNT + 1):
      text = "Testing AJAX response %d." % i
      post = Post(user=self.user, floor=self.floor, text=text)
      post.save()
    
    second_post = Post.objects.all().order_by("-pk")[0]
    response = self.client.get(reverse("news_more_posts"), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    self.failUnlessEqual(response.status_code, 200)
    self.assertNotContains(response, "Testing AJAX response 0.")
    self.assertContains(response, "See More")
    for i in range(1, DEFAULT_POST_COUNT + 1):
      self.assertContains(response, "Testing AJAX response %d" % i)
    
    response = self.client.get(reverse("news_more_posts") + ("?last_post=%d" % second_post.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    self.assertContains(response, "Testing AJAX response 0.")
      
      
      
    
    