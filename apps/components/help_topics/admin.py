from django.contrib import admin
from django import forms

from components.help_topics.models import HelpTopic

class HelpAdminForm(forms.ModelForm):
  class Meta:
    model = HelpTopic
    
  def clean_parent_topic(self):
    """
    Prevents sub-topics of sub-topics.  It cannot be done with the current template layout.
    """
    parent_topic = self.cleaned_data["parent_topic"]
    if parent_topic.parent_topic:
      raise forms.ValidationError("This topic is also a sub-topic. Sub-topics of sub-topics are not allowed.")
    return data
    
class HelpTopicAdmin(admin.ModelAdmin):
  # Automatically populates the slug field.
  prepopulated_fields = {"slug": ("title",)}
  
  form = HelpAdminForm

admin.site.register(HelpTopic, HelpTopicAdmin)