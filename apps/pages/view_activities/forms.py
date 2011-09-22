from django import forms
from django.forms.util import ErrorList

from components.activities.models import ConfirmationCode, QuestionChoice, TextReminder
from components.activities import *

class ActivityTextForm(forms.Form):
  question = forms.IntegerField(widget=forms.HiddenInput(), required=False)

  response = forms.CharField(widget=forms.Textarea(attrs={'rows':'2'}), required=True)
  comment = forms.CharField(widget=forms.Textarea(attrs={'rows':'3'}), required=False)
  social_email = forms.CharField(widget=forms.TextInput(attrs={'size':'30'}), required=False)
  social_email2 = forms.CharField(widget=forms.TextInput(attrs={'size':'30'}), required=False)

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

class ActivityCodeForm(forms.Form):
  response = forms.CharField(widget=forms.TextInput(attrs={'size':'15'}), required=True)
  comment = forms.CharField(widget=forms.Textarea(attrs={'rows':'3'}), required=False)
  social_email = forms.CharField(widget=forms.TextInput(attrs={'size':'30'}), required=False)
  social_email2 = forms.CharField(widget=forms.TextInput(attrs={'size':'30'}), required=False)

  def __init__(self, *args, **kwargs):
    self.request = kwargs.pop('request', None)
    self.activity = kwargs.pop('activity', None)

    super(ActivityCodeForm, self).__init__(*args, **kwargs)

  def clean(self):
    """Custom validation to verify confirmation codes."""
    cleaned_data = self.cleaned_data

    # Check if we are validating a confirmation code.
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

    _validate_social_email(self, cleaned_data)

    return cleaned_data

class ActivityFreeResponseForm(forms.Form):
  response = forms.CharField(widget=forms.Textarea)
  comment = forms.CharField(widget=forms.Textarea(attrs={'rows':'3'}), required=False)
  social_email = forms.CharField(widget=forms.TextInput(attrs={'size':'30'}), required=False)
  social_email2 = forms.CharField(widget=forms.TextInput(attrs={'size':'30'}), required=False)

  def __init__(self, *args, **kwargs):  
    self.request = kwargs.pop('request', None)
    self.activity = kwargs.pop('activity', None)
    super(ActivityFreeResponseForm, self).__init__(*args, **kwargs)  

  def clean(self):
    cleaned_data = self.cleaned_data
    _validate_social_email(self, cleaned_data)    
    return cleaned_data
    
class ActivityImageForm(forms.Form):
  image_response = forms.ImageField()
  comment = forms.CharField(widget=forms.Textarea(attrs={'rows':'3'}), required=False)
  social_email = forms.CharField(widget=forms.TextInput(attrs={'size':'30'}), required=False)
  social_email2 = forms.CharField(widget=forms.TextInput(attrs={'size':'30'}), required=False)

  def __init__(self, *args, **kwargs):  
    self.request = kwargs.pop('request', None)
    self.activity = kwargs.pop('activity', None)
    super(ActivityImageForm, self).__init__(*args, **kwargs)  

  def clean(self):
    cleaned_data = self.cleaned_data
    _validate_social_email(self, cleaned_data)    
    return cleaned_data

class ActivityFreeResponseImageForm(forms.Form):
  response = forms.CharField(widget=forms.Textarea)
  image_response = forms.ImageField()
  comment = forms.CharField(widget=forms.Textarea(attrs={'rows':'3'}), required=False)
  social_email = forms.CharField(widget=forms.TextInput(attrs={'size':'30'}), required=False)
  social_email2 = forms.CharField(widget=forms.TextInput(attrs={'size':'30'}), required=False)

  def __init__(self, *args, **kwargs):
    self.request = kwargs.pop('request', None)
    self.activity = kwargs.pop('activity', None)
    super(ActivityFreeResponseImageForm, self).__init__(*args, **kwargs)

  def clean(self):
    cleaned_data = self.cleaned_data
    _validate_social_email(self, cleaned_data)
    return cleaned_data

class CommitmentCommentForm(forms.Form):
  comment = forms.CharField(widget=forms.Textarea(attrs={'rows':'3'}), required=False)
  social_email = forms.CharField(widget=forms.TextInput(attrs={'size':'30'}), required=False)
  social_email2 = forms.CharField(widget=forms.TextInput(attrs={'size':'30'}), required=False)

  def __init__(self, *args, **kwargs):  
    self.request = kwargs.pop('request', None)
    self.activity = kwargs.pop('activity', None)
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
        self.fields['choice_response_%s' % i] = forms.ModelChoiceField(
            queryset=QuestionChoice.objects.filter(question__id=q.pk), 
            label=q.question, 
            required=True
        )
    
  def clean(self):
    cleaned_data = self.cleaned_data
    return cleaned_data
  
def _validate_social_email(self, cleaned_data):

  if self.activity.is_group and (not cleaned_data.has_key("social_email") or cleaned_data["social_email"]==None or cleaned_data["social_email"]==""):
    self._errors["social_email"] = ErrorList(["At least one email is required."])

  _validate_one_email(self, cleaned_data, "social_email")
  _validate_one_email(self, cleaned_data, "social_email2")

def _validate_one_email(self, cleaned_data, email):
  if cleaned_data[email]:
    user = get_user_by_email(cleaned_data[email])
    if user == None or user == self.request.user:
      self._errors[email] = ErrorList(["Invalid email. Please input only one valid email."])
      del cleaned_data[email]

class EventCodeForm(forms.Form):
  response = forms.CharField(widget=forms.TextInput(attrs={'size':'12'}))
  social_email = forms.CharField(widget=forms.TextInput(attrs={'size':'15'}), initial="Email", required=False)

#------ Reminder form ---------
from django.contrib.localflavor.us.forms import USPhoneNumberField

REMINDER_TIME_CHOICES = (
    ("1", "1 hour"),
    ("2", "2 hours"),
    ("3", "3 hours"),
    ("4", "4 hours"),
    ("5", "5 hours"),
)
class ReminderForm(forms.Form):
  send_email = forms.BooleanField(required=False)
  email = forms.EmailField(required=False, label="Email Address")
  send_text = forms.BooleanField(required=False)
  email_advance = forms.ChoiceField(choices=REMINDER_TIME_CHOICES, label="Send reminder how far in advance?")
  text_number = USPhoneNumberField(required=False, label="Mobile phone number")
  text_carrier = forms.ChoiceField(choices=TextReminder.TEXT_CARRIERS, required=False, label="Carrier")
  text_advance = forms.ChoiceField(choices=REMINDER_TIME_CHOICES, label="Send reminder how far in advance?")
    
  def clean(self):
    cleaned_data = self.cleaned_data
    send_email = cleaned_data.get("send_email")
    email = None
    if cleaned_data.has_key("email"):
      email = cleaned_data.get("email")
    if send_email and (not email or len(email) == 0):
      raise forms.ValidationError("A valid email address is required.")
      
    send_text = cleaned_data.get("send_text")
    number = None
    if cleaned_data.has_key("text_number"):
      number = cleaned_data.get("text_number")
    if send_text and (not number or len(number) == 0):
      raise forms.ValidationError("A valid phone number is required.")
      
    return cleaned_data
