from django.db import models
from django.contrib.auth.models import User

from components.activities.models import ActivityBase

# Create your models here.
class Mission(models.Model):
  name = models.CharField(max_length=255, help_text="Title of the mission.")
  slug = models.SlugField(help_text="Automatically generated in the admin.")
  description = models.TextField(help_text="Description of the mission.")
  users = models.ManyToManyField(User, through='MissionMember', editable=False)
  activities = models.ManyToManyField(ActivityBase, related_name="missionactivities")
  created_at = models.DateTimeField(auto_now_add=True, editable=False)
  updated_at = models.DateTimeField(auto_now=True, editable=False)
  
  def __unicode__(self):
    return self.name
  
class MissionMember(models.Model):
  user = models.ForeignKey(User)
  mission = models.ForeignKey(Mission)
  completed = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True, editable=False)
  updated_at = models.DateTimeField(auto_now=True, editable=False)
  
class Post(models.Model):
  user = models.ForeignKey(User, related_name="canopyposts")
  text = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True, editable=False)

