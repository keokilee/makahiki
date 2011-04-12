import sys

from django.contrib import admin
from django import forms
from django.contrib.auth.models import User

from components.quests.models import Quest

class QuestAdminForm(forms.ModelForm):
  class Meta:
    model = Quest
    
  def clean_unlock_conditions(self):
    """
    Validates the unlock conditions of the quest.
    """
    from components.quests import process_conditions_string
    
    data = self.cleaned_data["unlock_conditions"]
    # Pick a user and see if the conditions result is true or false.
    user = User.objects.all()[0]
    try:
      result = process_conditions_string(data, user)
      # Check if the result type is a boolean
      if type(result) != type(True):
        raise forms.ValidationError("Expected boolean value but got %s" % type(result))
    except Exception:
      raise forms.ValidationError("Received exception: %s" % sys.exc_info()[0])
      
    return data
    
  def clean_completion_conditions(self):
    """
    Validates the unlock conditions of the quest.
    """
    from components.quests import process_conditions_string
    
    data = self.cleaned_data["completion_conditions"]
    # Pick a user and see if the conditions result is true or false.
    user = User.objects.all()[0]
    try:
      result = process_conditions_string(data, user)
      # Check if the result type is a boolean
      if type(result) != type(True):
        raise forms.ValidationError("Expected boolean value but got %s" % type(result))
    except Exception:
      raise forms.ValidationError("Received exception: %s" % sys.exc_info()[0])

    return data
  
  
class QuestAdmin(admin.ModelAdmin):
  # Automatically populates the slug field.
  prepopulated_fields = {"quest_slug": ("name",)}
  
  form = QuestAdminForm
  
admin.site.register(Quest, QuestAdmin)