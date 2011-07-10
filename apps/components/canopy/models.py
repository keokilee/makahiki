from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Quest(models.Model):
  title = models.CharField(max_length=255, help_text="Title of the quest.")
  slug = models.SlugField(help_text="Automatically generated in the admin.")
  description = models.TextField(help_text="Description of the quest.")
  users = models.ManyToManyField(User, related_name="canopyquest", editable=False)
  created_at = models.DateTimeField(auto_now_add=True, editable=False)
  updated_at = models.DateTimeField(auto_now=True, editable=False)
  
class Post(models.Model):
  user = models.ForeignKey(User, related_name="canopypost")
  text = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True, editable=False)

