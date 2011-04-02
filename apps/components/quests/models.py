from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Quest(models.Model):
  """
  Represents a quest in the database.
  """
  name = models.CharField(max_length=255, help_text="The name of the quest.")
  quest_slug = models.SlugField()
  description = models.TextField(help_text="Outline the steps to completing this quest.")
  level = models.IntegerField()
  unlock_conditions = models.TextField(
      help_text="Conditions a user needs to meet in order to have this quest be available."
  )
  completion_conditions = models.TextField(
      help_text="Conditions a user needs to meet in order to complete the quest."
  )
  users = models.ManyToManyField(User, through="QuestMember")
  created_at = models.DateTimeField(auto_now_add=True, editable=False)
  updated_at = models.DateTimeField(auto_now=True, editable=False)
  
  def __unicode__(self):
    return self.name
  
class QuestMember(models.Model):
  """
  Represents a user's participation in a quest.
  This should not be in the admin interface, since there shouldn't be a reason to edit instances.
  """
  user = models.ForeignKey(User)
  quest = models.ForeignKey(Quest)
  completed = models.BooleanField(default=False, help_text="True if the user completed the quest.")
  opt_out = models.BooleanField(default=False, help_text="True if the user opts out of the quest.")
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)