from django import forms
from django.contrib.localflavor.us.forms import USPhoneNumberField

from components.makahiki_profiles.models import Profile

class ProfileForm(forms.Form):
  display_name = forms.CharField(required=True)
  about = forms.CharField(required=False, widget=forms.Textarea(attrs={
    "class": "span-5",
    "style": "height: 40px",
  }))
  # TODO: check http://docs.djangoproject.com/en/dev/topics/http/sessions/#using-sessions-in-views
  stay_logged_in = forms.BooleanField(initial=True)
  
  facebook_enabled = forms.BooleanField()
  facebook_can_post = forms.BooleanField()
  
  # Event notifications
  event_can_email = forms.BooleanField()
  event_email = forms.EmailField(required=False)
  event_can_text = forms.BooleanField()
  event_text = USPhoneNumberField(required=False, widget=forms.TextInput(attrs={
    "style": "width: 100px",
  }))
  event_text_carrier = forms.ChoiceField(choices=(
    ("t-mobile", "T-Mobile"),
    ("att", "AT&T"),
    ("sprint", "Sprint"),
    ("verizon", "Verizon"),
  ))
  
  # Alert notifications
  alert_can_email = forms.BooleanField()
  alert_email = forms.EmailField(required=False)
  alert_can_text = forms.BooleanField()
  alert_text = USPhoneNumberField(required=False, widget=forms.TextInput(attrs={
    "style": "width: 100px",
  }))
  alert_text_carrier = forms.ChoiceField(choices=(
    ("t-mobile", "T-Mobile"),
    ("att", "AT&T"),
    ("sprint", "Sprint"),
    ("verizon", "Verizon"),
  ))
  
