from django import forms
from django.forms.util import ErrorList

from components.activities.models import ConfirmationCode
from components.activities.models import QuestionChoice
from components.activities import *

class ActivityTextForm(forms.Form):
  question = forms.IntegerField(widget=forms.HiddenInput(), required=False)
  code = forms.IntegerField(widget=forms.HiddenInput(), required=False)
  
  response = forms.CharField(widget=forms.Textarea(attrs={'rows':'2'}), required=True)
  comment = forms.CharField(widget=forms.Textarea(attrs={'rows':'3'}), required=False)
  social_email = forms.CharField(widget=forms.TextInput(attrs={'size':'40'}), required=False)
  
  def __init__(self, *args, **kwargs):  
    self.request = kwargs.pop('request', None)
    self.activity = kwargs.pop('activity', None)
    qid = None
    if 'question_id' in kwargs:
      qid = kwargs.pop('question_id')
      
    super(ActivityTextForm, self).__init__(*args, **kwargs)  
    
    if qid:
      self.fields['choice_response'] = forms.ModelChoiceField(queryset=QuestionChoice.objects.filter(question__id=qid), required=True)

  def clean(self):
    """Custom validation to verify confirmation codes."""
    cleaned_data = self.cleaned_data
    
    # Check if we are validating a confirmation code.
    if cleaned_data["code"]==1:
      try:
        code = ConfirmationCode.objects.get(code=cleaned_data["response"])
        # Check if the code is inactive.
        if not code.is_active:
          self._errors["response"] = ErrorList(["This code has already been used."])
          del cleaned_data["response"]
        # Check if this activity is the same as the added activity (if provided)
        elif self.activity and code.activity != self.activity:
          self._errors["response"] = ErrorList(["This confirmation code is not valid for this activity."])
          del cleaned_data["response"]
        # Check if the user has already submitted a code for this activity.
        elif code.activity in self.request.user.activity_set.filter(activitymember__award_date__isnull=False):
          self._errors["response"] = ErrorList(["You have already redemmed a code for this activity."])
          del cleaned_data["response"]
      except ConfirmationCode.DoesNotExist:
        self._errors["response"] = ErrorList(["This code is not valid."])
        del cleaned_data["response"]
      except KeyError:
        self._errors["response"] = ErrorList(["Please input code."])

    # Check if we are validating quetion
    if cleaned_data["question"]>0:
        if (not cleaned_data.has_key("response")) and (not cleaned_data.has_key("choice_response")):
          self._errors["response"] = ErrorList(["You need to answer the question."])
          if cleaned_data.has_key("response"):
            del cleaned_data["response"]
          if cleaned_data.has_key("choice_response"):
            del cleaned_data["choice_response"]
    
    _validate_social_email(self, cleaned_data)    
          
    return cleaned_data
  
class ActivityFreeResponseForm(forms.Form):
  response = forms.CharField(widget=forms.Textarea)
  comment = forms.CharField(widget=forms.Textarea(attrs={'rows':'3'}), required=False)
  social_email = forms.CharField(widget=forms.TextInput(attrs={'size':'40'}), required=False)

  def __init__(self, *args, **kwargs):  
    self.request = kwargs.pop('request', None)
    super(ActivityFreeResponseForm, self).__init__(*args, **kwargs)  
  
  def clean(self):
    cleaned_data = self.cleaned_data
    _validate_social_email(self, cleaned_data)    
    return cleaned_data
    
class ActivityImageForm(forms.Form):
  image_response = forms.ImageField()
  comment = forms.CharField(widget=forms.Textarea(attrs={'rows':'3'}), required=False)
  social_email = forms.CharField(widget=forms.TextInput(attrs={'size':'40'}), required=False)

  def __init__(self, *args, **kwargs):  
    self.request = kwargs.pop('request', None)
    super(ActivityImageForm, self).__init__(*args, **kwargs)  

  def clean(self):
    cleaned_data = self.cleaned_data
    _validate_social_email(self, cleaned_data)    
    return cleaned_data
    
class CommitmentCommentForm(forms.Form):
  comment = forms.CharField(widget=forms.Textarea(attrs={'rows':'3'}), required=False)
  social_email = forms.CharField(widget=forms.TextInput(attrs={'size':'40'}), required=False)

  def __init__(self, *args, **kwargs):  
    self.request = kwargs.pop('request', None)
    super(CommitmentCommentForm, self).__init__(*args, **kwargs)  

  def clean(self):
    cleaned_data = self.cleaned_data
    _validate_social_email(self, cleaned_data)
    return cleaned_data
    
class SurveyForm(forms.Form):  
  def __init__(self, *args, **kwargs):  
    questions = None
    if 'questions' in kwargs:
      questions = kwargs.pop('questions')
      
    super(SurveyForm, self).__init__(*args, **kwargs)
    
    if questions:
      for i, q in enumerate(questions):
        self.fields['choice_response_%s' % i] = forms.ModelChoiceField(queryset=QuestionChoice.objects.filter(question__id=q.pk), label=q.question, required=True)
    
  def clean(self):
    cleaned_data = self.cleaned_data
    return cleaned_data
    
def _validate_social_email(self, cleaned_data):
  
  if cleaned_data["social_email"]:
    user = get_user_by_email(cleaned_data["social_email"]) 
    if user == None or user == self.request.user:
      self._errors["social_email"] = ErrorList(["Invalid email. Please input only one valid email."])
      del cleaned_data["social_email"]
