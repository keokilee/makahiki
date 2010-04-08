from activities.models import Activity, ActivityMember, TextPromptQuestion
from django.contrib import admin
from django.forms import ModelForm, ValidationError
from django.forms.models import BaseInlineFormSet
from django.forms.util import ErrorList
  
class ActivityAdminForm(ModelForm):
  class Meta:
    model = Activity
    
  def clean(self):
    """ Validates the admin form data based on our constraints.
      
      #1 Events must have an event date.
      #2 If the verification type is "image" or "code", then a confirm prompt is required.
      #3 If the verification type is "text", then additional questions are required 
         (Handled in the formset class below).
      #4 Publication date must be before expiration date. """
    
    # Data that has passed validation.
    cleaned_data = self.cleaned_data
    
    #1 Check that an event has an event date.
    is_event = cleaned_data.get("is_event")
    event_date = cleaned_data.get("event_date")
    has_date = cleaned_data.has_key("event_date") #Check if this is in the data dict.
    
    if is_event and has_date and not event_date:
      self._errors["event_date"] = ErrorList([u"Events require an event date."])
      del cleaned_data["is_event"]
      del cleaned_data["event_date"]
      
    #2 Check the verification type.
    confirm_type = cleaned_data.get("confirm_type")
    prompt = cleaned_data.get("confirm_prompt")
    if confirm_type != "text" and len(prompt) == 0:
      self._errors["confirm_prompt"] = ErrorList([u"This confirmation type requires a confirmation prompt."])
      del cleaned_data["confirm_type"]
      del cleaned_data["confirm_prompt"]
      
    #4 Publication date must be before the expiration date.
    if cleaned_data.has_key("pub_date") and cleaned_data.has_key("expire_date"):
      pub_date = cleaned_data.get("pub_date")
      expire_date = cleaned_data.get("expire_date")
      
      if pub_date >= expire_date:
        self._errors["expire_date"] = ErrorList([u"The expiration date must be after the pub date."])
        del cleaned_data["expire_date"]
      
    return cleaned_data
    
class TextQuestionInlineFormSet(BaseInlineFormSet):
  """Custom formset model to override validation."""
  
  def clean(self):
    """Validates the form data and checks if the activity confirmation type is text."""
    
    # Form that represents the activity.
    activity_form = self.instance
    
    # Count the number of questions.
    count = 0
    for form in self.forms:
      try:
        if form.cleaned_data:
          count += 1
      except AttributeError:
        pass
        
    if activity_form.confirm_type == "text" and count == 0:
      raise ValidationError("At least one question is required if the activity's confirmation type is text.")
        
    elif activity_form.confirm_type != "text" and count > 0:
      raise ValidationError("Questions are not required for this confirmation type.")

class TextQuestionInline(admin.StackedInline):
  model = TextPromptQuestion
  extra = 3
  formset = TextQuestionInlineFormSet
  
class ActivityAdmin(admin.ModelAdmin):
  form = ActivityAdminForm
  inlines = [TextQuestionInline]
  
admin.site.register(Activity, ActivityAdmin)
admin.site.register(ActivityMember)
