import datetime
import string

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

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
  floor_number = models.IntegerField(help_text="The floor number in the dorm.")
  dorm = models.ForeignKey(Dorm, help_text="The dorm this floor belongs to.")
  
  def __unicode__(self):
    return "%s: Floor %d" % (self.dorm.name, self.floor_number)
  