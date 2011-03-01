from django import forms
from django.forms.util import ErrorList

from components.activities.models import ConfirmationCode
from components.activities.models import QuestionChoice

class ActivityTextForm(forms.Form):
  question = forms.IntegerField(widget=forms.HiddenInput(), required=False)
  code = forms.IntegerField(widget=forms.HiddenInput(), required=False)
  
  response = forms.CharField(max_length=255, required=False)
  comment = forms.CharField(widget=forms.Textarea(attrs={'rows':'5'}), required=False)
  
  def __init__(self, *args, **kwargs):  
    qid = None
    if 'question_id' in kwargs:
      qid = kwargs.pop('question_id')
      
    super(ActivityTextForm, self).__init__(*args, **kwargs)  
    
    if qid:
      self.fields['choice_response'] = forms.ModelChoiceField(queryset=QuestionChoice.objects.filter(question__id=qid), required=False)

  def clean(self):
    """Custom validation to verify confirmation codes."""
    cleaned_data = self.cleaned_data
    
    # Check if we are validating a confirmation code.
    if cleaned_data["code"]==1:
      try:
        code = ConfirmationCode.objects.get(code=cleaned_data["response"])
        if not code.is_active:
          self._errors["response"] = ErrorList(["This code has already been used."])
          del cleaned_data["response"]
      except ConfirmationCode.DoesNotExist:
        self._errors["response"] = ErrorList(["This code is not valid."])
        del cleaned_data["response"]
      except KeyError:
        self._errors["response"] = ErrorList(["Please input code."])

    # Check if we are validating quetion
    if cleaned_data["question"]>0:
        if (not cleaned_data.has_key("response")) and (not cleaned_data.has_key("choice_response")):
          self._errors["question"] = ErrorList(["You need to answer the question."])
          if cleaned_data.has_key("response"):
            del cleaned_data["response"]
          if cleaned_data.has_key("choice_response"):
            del cleaned_data["choice_response"]
        
    return cleaned_data
  
class ActivityFreeResponseForm(forms.Form):
  response = forms.CharField(widget=forms.Textarea)
  comment = forms.CharField(widget=forms.Textarea, required=False)
  
class ActivityImageForm(forms.Form):
  image_response = forms.ImageField()
  comment = forms.CharField(widget=forms.Textarea, required=False)
  
class CommitmentCommentForm(forms.Form):
  comment = forms.CharField(widget=forms.Textarea, required=False)
