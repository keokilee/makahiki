import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.template.defaultfilters import slugify

from floors.models import Floor

# Create your models here.

class Like(models.Model):
  """Tracks the objects that users like."""
  user = models.ForeignKey(User)
  floor = models.ForeignKey(Floor)
  content_type = models.ForeignKey(ContentType)
  object_id = models.IntegerField()
  content_object = generic.GenericForeignKey('content_type', 'object_id')

class Article(models.Model):
  """Represents an article on the front page."""
  prepopulated_fields = {"slug": ("title",)}
  
  title = models.CharField(max_length=255)
  slug = models.SlugField(max_length=50, blank=True, help_text="Automatically generated if left blank.")
  abstract = models.TextField(help_text="Short description of the story.  Uses Markdown formatting.")
  content = models.TextField(help_text="Uses Markdown formatting.")
  created_at = models.DateTimeField(editable=False)
  updated_at = models.DateTimeField(null=True, editable=False)
  
  def __unicode__(self):
    return self.title
    
  def formatted_date(self):
    """Formats the created or updated date into a pretty string."""
    date = self.updated_at or self.created_at
    return date.strftime("%m/%d %I:%M %p")
    
  def save(self):
    """Custom save method to update slug and date time fields and to post headlines."""
    
    if not self.slug:
      self.slug = slugify(self.title)
    
    if not self.id:
      self.created_at = datetime.datetime.today()
    else:
      self.updated_at = datetime.datetime.today()

    super(Article, self).save()
    