import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from groups.base import Group

# Create your models here.

class Dorm(models.Model):
  name = models.CharField(max_length=200)
  slug = models.CharField(max_length=20, blank=True)
  created_at = models.DateTimeField(editable=False);
  updated_at = models.DateTimeField(null=True, editable=False)
  
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
    
    if not created_at:
      created_at = datetime.date.today()
    else:
      updated_at = datetime.date.today()
      
    super(Dorm, self).save()
    
class Floor(Group):
  floor_number = models.IntegerField()
  dorm = models.ForeignKey(Dorm)
  members = models.ManyToManyField(User, related_name='floors', verbose_name=_('members'))
  