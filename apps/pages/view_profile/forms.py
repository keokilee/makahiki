from django import forms
from django.contrib.localflavor.us.forms import USPhoneNumberField

from components.makahiki_profiles.models import Profile

class ProfileForm(forms.Form):
  display_name = forms.CharField(required=True)
  enable_help = forms.BooleanField(required=False)
  # TODO: check http://docs.djangoproject.com/en/dev/topics/http/sessions/#using-sessions-in-views
  stay_logged_in = forms.BooleanField(initial=True)
  
  facebook_can_post = forms.BooleanField(required=False)
  
  # Event notifications
  contact_email = forms.EmailField(required=False)
  contact_text = USPhoneNumberField(required=False, widget=forms.TextInput(attrs={
    "style": "width: 100px",
  }))
  contact_carrier = forms.ChoiceField(choices=(
    ("t-mobile", "T-Mobile"),
    ("att", "AT&T"),
    ("sprint", "Sprint"),
    ("verizon", "Verizon"),
  ))

  
