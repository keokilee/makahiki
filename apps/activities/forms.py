from django import forms
from django.forms.util import ErrorList

from activities.models import ConfirmationCode

class ActivityTextForm(forms.Form):
  response = forms.CharField(max_length=255)
  comment = forms.CharField(widget=forms.Textarea, required=False)
  question = forms.IntegerField(widget=forms.HiddenInput(), required=False)
  
  def clean(self):
    """Custom validation to verify confirmation codes."""
    cleaned_data = self.cleaned_data
    
    # Check if we are validating a confirmation code.
    if not cleaned_data.has_key("question"):
      try:
        code = ConfirmationCode.objects.get(code=cleaned_data["response"])
        if not code.is_active:
          self._errors["response"] = ErrorList(["This code has already been used."])
          del cleaned_data["response"]
      except ConfirmationCode.DoesNotExist:
        self._errors["response"] = ErrorList(["This code is not valid."])
        del cleaned_data["response"]
      
    return cleaned_data
  
class ActivityImageForm(forms.Form):
  image_response = forms.ImageField()
  comment = forms.CharField(widget=forms.Textarea, required=False)
  
class CommitmentCommentForm(forms.Form):
  comment = forms.CharField(widget=forms.Textarea, required=False)
  
class GoalCommentForm(forms.Form):
  comment = forms.CharField(widget=forms.Textarea, required=False)