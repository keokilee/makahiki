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
  floor_number = models.IntegerField(help_text="The floor number in the dorm.")
  dorm = models.ForeignKey(Dorm, help_text="The dorm this floor belongs to.")
  chart_url = models.CharField(
                  max_length=200,
                  blank=True, 
                  null=True,
                  help_text="Specify a Google Chart where we can retrieve power and energy data from."
  )
  
  chart_dorm = models.CharField(
                  max_length=200,
                  blank=True,
                  null=True,
                  help_text="The column value where we can find the dorm in the Google chart."
  )
  
  chart_floor = models.CharField(
                  max_length=200,
                  blank=True,
                  null=True,
                  help_text="The column value where we can find the floor in the Google chart."
  )
  
  def __unicode__(self):
    return "%s: Floor %d" % (self.dorm.name, self.floor_number)
    
  def get_wattdepot_host(self):
    """Retrieves the floor's specified host or the host specified in settings."""
    return self.wattdepot_host or settings.WATTDEPOT_HOST
  