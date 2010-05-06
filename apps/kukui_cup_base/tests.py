import unittest

from kukui_cup_base.models import Article

class ArticleTestCase(unittest.TestCase):
  def testCreateSlug(self):
    article = Article(title="Hello World!", content="What's up everyone?")
    slug = article.create_slug()
    self.assertEqual("hello-world", slug, "Testing that slug strips punctuation.")
    
    article.title = ""
    for i in range(0, 255):
      article.title += "x"
      
    slug = article.create_slug()
    self.assertTrue(len(slug) < len(article.title), "Testing that slug shortens title.")
    
  def testDateSlug(self):
    article = Article(title="Standings for 4/18", content="Currently, Frear Hall is in the lead!")
    article.save()
    self.assertEqual("standings-for-418", article.slug, "Testing creating a slug from a date.")