import datetime

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
    response = self.client.get(reverse("news_index"))
    self.failUnlessEqual(response.status_code, 200)
    
  def testIndexCommitment(self):
    """Tests that a commitment shows up in public commitments and in the wall."""
    posts = self.floor.post_set.count()
    # Create a commitment that will appear on the news page.
    commitment = Commitment(
                type="commitment",
                title="Test commitment",
                description="A commitment!",
                point_value=10,
    )
    commitment.save()
    
    member = CommitmentMember(commitment=commitment, user=self.user)
    member.save()
    
    response = self.client.get(reverse("news_index"))
    self.failUnlessEqual(response.status_code, 200)
    self.assertEqual(posts + 1, self.floor.post_set.count(), "One post should have been posted to the wall (public commitment).")
    self.assertContains(response, commitment.title, 2, 
        msg_prefix="Commitment title should only appear in the wall and the public commitments box."
    )
    
  def testIndexMostPopular(self):
    posts = self.floor.post_set.count()
    commitment = Commitment(
                type="commitment",
                title="Test commitment",
                description="A commitment!",
                point_value=10,
    )
    commitment.save()
    
    member = CommitmentMember(commitment=commitment, user=self.user, award_date=datetime.datetime.today())
    member.save()
    
    response = self.client.get(reverse("news_index"))
    self.failUnlessEqual(response.status_code, 200)
    self.assertEqual(posts + 2, self.floor.post_set.count(), "Two posts should have been posted to the wall (commit and award).")
    self.assertContains(response, commitment.title, 3, 
        msg_prefix="""
        Commitment title should appear in the wall twice and in the most popular box. Note, may fail because of caching.
        """
    )
    
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
    self.assertContains(response, "See more")
    for i in range(1, DEFAULT_POST_COUNT + 1):
      self.assertContains(response, "Testing AJAX response %d" % i)
    
    response = self.client.get(reverse("news_more_posts") + ("?last_post=%d" % second_post.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    self.assertContains(response, "Testing AJAX response 0.")
    