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
    from components.quests import CONDITIONS
    
    conditions = self.unlock_conditions
    for name in CONDITIONS.keys():
      conditions = conditions.replace(name + "(", name + "(user,")
      
    allow_dict = CONDITIONS.copy()
    allow_dict.update({"True": True, "False": False, "user": user})
    
    return eval(conditions, {"__builtins__":None}, allow_dict)
    
  def completed_quest(self, user):
    """Returns True if the user completed the quest."""
    from components.quests import CONDITIONS
    
    conditions = self.completion_conditions
    for name in CONDITIONS.keys():
      conditions = conditions.replace(name + "(", name + "(user,")
      
    allow_dict = CONDITIONS.copy()
    allow_dict.update({"True": True, "False": False, "user": user})
    
    return eval(conditions, {"__builtins__":None}, allow_dict)
    
  def accept(self, user):
    """
    Lets the user accept the quest.  Returns True if successful.
    """
    # Check if this quest is in the list.
    if self in user.quest_set.all():
      return False
      
    member = QuestMember(quest=self, user=user)
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