from django import forms
from django.contrib.localflavor.us.forms import USPhoneNumberField

from components.activities.models import TextReminder

class ProfileForm(forms.Form):
  display_name = forms.CharField(required=True)
  enable_help = forms.BooleanField(required=False)
  # TODO: check http://docs.djangoproject.com/en/dev/topics/http/sessions/#using-sessions-in-views
  stay_logged_in = forms.BooleanField(initial=True)
  
  # Event notifications
  contact_email = forms.EmailField(required=False)
  contact_text = USPhoneNumberField(required=False, widget=forms.TextInput(attrs={
    "style": "width: 100px",
  }))
  contact_carrier = forms.ChoiceField(choices=TextReminder.TEXT_CARRIERS)
  
  # def clean_display_name(self):
  #   """
  #   Validates the display name of the user.
  #   
  #   This needs to be implemented since some DBs (SQLite) do not have the ability to add unique constraints.
  #   """
  #   data = self.cleaned_data['display_name']
  #   try:
  #     profile = Profile.objects.get(name=data.strip())
  #     raise forms.ValidationError("'%s' is taken, please enter another name." % data)
  #   except Profile.DoesNotExist:
  #     pass
  #     
  #   return data

  
