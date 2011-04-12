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
    
  def can_add_quest(self, user):
    """Returns True if the user can add the quest."""
    from components.quests import process_conditions_string
    
    return process_conditions_string(self.unlock_conditions, user)
    
  def completed_quest(self, user):
    """Returns True if the user completed the quest."""
    from components.quests import process_conditions_string
    
    return process_conditions_string(self.completion_conditions, user)
    
  def accept(self, user):
    """
    Lets the user accept the quest.  Returns True if successful.
    """
    # Check if user can add the quest.
    if not self.can_add_quest(user):
      return False
      
    # Check if this quest is in their list of quests.
    if self in user.quest_set.all():
      return False
      
    member = QuestMember(quest=self, user=user)
    member.save()
    return True
    
  def opt_out(self, user):
    """
    Lets the user opt out of seeing the quest.  Returns True if successful.
    """
    # Check if user can add the quest.
    if not self.can_add_quest(user):
      return False
      
    # Note in this case, we don't care if the user already has the quest.
    member, created = QuestMember.objects.get_or_create(quest=self, user=user)
    member.opt_out = True
    member.save()
    return True
  
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
  
  class Meta:
    unique_together = ["user", "quest"]