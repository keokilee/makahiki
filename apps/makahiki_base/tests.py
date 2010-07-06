from django.test import TestCase

from makahiki_base.models import Article, Headline

class ArticleTestCase(TestCase):
  fixtures = ["base_data.json", "user_data.json"]
  
  def testCreateSlug(self):
    """Tests creating slugs."""
    article = Article(title="Hello World!", content="What's up everyone?")
    slug = article.create_slug()
    self.assertEqual("hello-world", slug, "Testing that slug strips punctuation.")
    
    article.title = ""
    for i in range(0, 255):
      article.title += "x"
      
    slug = article.create_slug()
    self.assertTrue(len(slug) < len(article.title), "Testing that slug shortens title.")
    
  def testDateSlug(self):
    """Tests creating slugs with forward slashes."""
    article = Article(title="Standings for 4/18", content="Currently, Frear Hall is in the lead!")
    article.save()
    self.assertEqual("standings-for-418", article.slug, "Testing creating a slug from a date.")
    
  def testArticleHeadline(self):
    """Tests that an article headline is created for new stories and not old stories."""
    headline_count = len(Headline.objects.all())
    
    article = Article(
            title="Blue Planet Foundation", 
            content="There will be a Blue Planet Foundation meeting on campus at 2PM.  All are welcome to attend."
    )
    article.save()
    self.assertEqual(len(Headline.objects.all()), headline_count + 1, "Checking that a new headline is created.")
    
    article.content = "Editing content."
    article.save()
    self.assertEqual(len(Headline.objects.all()), headline_count + 1, "Check that another headline is not added.")