from django.db import models
import datetime

# Create your models here.
class Topic(models.Model):
  topic = models.CharField(max_length=255)
  
  def __unicode__(self):
    return self.topic

class Resource(models.Model):
  MEDIA_TYPES = (
    ('website', 'Website'),
    ('video', 'Video'),
    ('audio', 'Audio'),
    ('blog_post', 'Blog Posting'),
    ('news', 'News'),
    ('article', 'Article'),
  )
  
  created_at = models.DateTimeField(
    default=datetime.datetime.today(),
    editable=False,
  )
  updated_at = models.DateTimeField(
    default=datetime.datetime.today(),
    editable=False,
  )
  title = models.CharField(
    max_length=255,
    help_text="The title of the resource.",
  )
  abstract = models.TextField(
    help_text="A one paragraph, concise summary of the contents. Uses <a href=\"http://daringfireball.net/projects/markdown/\" target=\"_blank\">Markdown</a> formatting.",
  )
  topics = models.ManyToManyField(Topic)
  media_type = models.CharField(
    max_length=50, 
    choices=MEDIA_TYPES,
    help_text="The format of the resource."
  )
  length = models.IntegerField(
    null=True,
    blank=True,
    help_text="If appropriate, specify length in the approximate number of pages (for text), minutes duration for video/audio resources.",
  )
  url = models.URLField(
    help_text="Provide the full URL (beginning with http:) to this resource.",
  )
  added_by = models.CharField(
    max_length=255,
    help_text="Please put your first name here so we know who entered this info in case we have questions later."
  )
  
  def __unicode__(self):
    return self.title
    
  def save(self):
    """Custom save method to update the updated_at field."""
    self.updated_at = datetime.datetime.today()
    super(Resource, self).save()
  