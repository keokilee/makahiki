import datetime
import string

from django.db import models

# Create your models here.

class Article(models.Model):
  """Represents an article on the front page."""
  
  title = models.CharField(max_length=255)
  slug = models.CharField(max_length=50, blank=True, help_text="Automatically generated if left blank.")
  abstract = models.TextField(help_text="Short description of the story.  Uses Markdown formatting.")
  content = models.TextField(help_text="Uses Markdown formatting.")
  created_at = models.DateTimeField(editable=False)
  updated_at = models.DateTimeField(null=True, editable=False)
  
  def __unicode__(self):
    return self.title
  
  def create_slug(self):
    """Creates a slug (an url parameter based on content of the article) from the article's title.
    Returns None if the article has no title."""
    
    if not self.title:
      return None
      
    if self.slug:
      return self.slug
    
    slug = self.title
    for char in string.punctuation:
      slug = slug.replace(char, "")
    slug = string.join(slug.split(), "-").lower()
    if len(slug) > 50:
      slug = slug[:50]
    
    return slug
    
  def formatted_date(self):
    """Formats the created or updated date into a pretty string."""
    date = self.updated_at or self.created_at
    return date.strftime("%m/%d %I:%M")
    
  def save(self):
    """Custom save method to update slug and date time fields."""
    
    if not self.slug:
      self.slug = self.create_slug()
    
    if not self.id:
      self.created_at = datetime.datetime.today()
    else:
      self.updated_at = datetime.datetime.today()
      
    super(Article, self).save()