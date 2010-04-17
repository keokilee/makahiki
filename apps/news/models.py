import datetime

from django.db import models

# Create your models here.

class Article(models.Model):
  """Represents an article on the front page."""
  
  title = models.CharField(max_length=255)
  slug = models.CharField(max_length=255, required=False)
  content = models.TextField(help_text="Uses Markdown formatting.")
  created_at = models.DateTimeField(editable=False)
  updated_at = models.DateTimeField(null=True, editable=False)
  
  def create_slug(self):
    """Creates a slug (an url based on content of the article) from the article's title.
    Returns None if the article has no title."""
    
    if not title:
      return None
      
    if self.slug:
      return self.slug
    
    slug = join(title.split(), "-").lower()
    
    return slug
    
  def save(self):
    """Custom save method to update slug and date time fields."""
    
    if not self.slug:
      self.slug = self.create_slug()
    
    if not self.id:
      self.created_at = datetime.datetime.today()
    else:
      self.updated_at = datetime.datetime.today()
      
    super(Article, self).save()
      