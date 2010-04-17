import unittest

from news.models import Article

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