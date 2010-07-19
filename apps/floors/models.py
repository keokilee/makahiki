import datetime
import string

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from groups.base import Group

# Create your models here.

class Dorm(models.Model):
  name = models.CharField(max_length=200, help_text="The name of the dorm.")
  slug = models.CharField(max_length=20, blank=True, help_text="Automatically generated if left blank.")
  created_at = models.DateTimeField(editable=False);
  updated_at = models.DateTimeField(null=True, editable=False)
  
  def __unicode__(self):
    return self.name
  
  def create_slug(self):
    """Creates a slug (a url parameter based on content of the title).
    Returns None if the floor has no title."""
    
    if not self.name:
      return None
      
    if self.slug:
      return self.slug
    
    slug = self.name
    for char in string.punctuation:
      slug = slug.replace(char, "")
    slug = string.join(slug.split(), "-").lower()
    if len(slug) > 20:
      slug = slug[:20]
    
    return slug
    
  def save(self):
    """Custom save method to generate slug and set created_at/updated_at."""
    if not self.slug:
      self.slug = self.create_slug()
    
    if not self.created_at:
      self.created_at = datetime.date.today()
    else:
      self.updated_at = datetime.date.today()
      
    super(Dorm, self).save()
    
class Floor(models.Model):
  number = models.CharField(help_text="The floor number in the dorm. Can be a string value", max_length=10)
  slug = models.CharField(max_length=10, blank=True, help_text="Automatically generated if left blank.")
  dorm = models.ForeignKey(Dorm, help_text="The dorm this floor belongs to.")
  floor_identifier = models.CharField(
                  max_length=200,
                  blank=True,
                  null=True,
                  help_text="Name of the variable used in the kukuicup configuration to refer to this floor."
  )
  
  def __unicode__(self):
    return "%s: Floor %s" % (self.dorm.name, self.slug)
    
  def create_slug(self):
    """Creates a slug (a url parameter based on content of the title).
    Returns None if the floor has no title."""

    if not self.number:
      return None

    if self.slug:
      return self.slug

    slug = self.number
    for char in string.punctuation:
      slug = slug.replace(char, "")
    slug = string.join(slug.split(), "-").lower()
    if len(slug) > 10:
      slug = slug[:10]

    return slug
    
  def save(self):
    """Custom save method to generate slug and set created_at/updated_at."""
    if not self.slug:
      self.slug = self.create_slug()

    super(Floor, self).save()
    
  def get_wattdepot_host(self):
    """Retrieves the floor's specified host or the host specified in settings."""
    return self.wattdepot_host or settings.WATTDEPOT_HOST
    
class Post(models.Model):
  """Represents a wall post on a user's wall."""
  user = models.ForeignKey(User)
  floor = models.ForeignKey(Floor)
  text = models.TextField()
  style_class = models.CharField(max_length=50, default="user_post") #CSS class to apply to this post.
  created_at = models.DateTimeField(editable=False)
  
  def date_string(self):
    """Formats the created date into a pretty string."""
    return self.created_at.strftime("%m/%d %I:%M %p")
  
  def save(self):
    if not self.created_at:
      self.created_at = datetime.datetime.today()
    
    super(Post, self).save()
  
class PostComment(models.Model):
  user = models.ForeignKey(User)
  post = models.ForeignKey(Post)
  text = models.TextField()
  created_at = models.DateTimeField(editable=False)
  
  def save(self):
    if not self.created_at:
      self.created_at = datetime.date.today()
    
    super(PostComment, self).save()