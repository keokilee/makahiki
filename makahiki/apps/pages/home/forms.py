import re

from django import forms
from django.conf import settings
from django.contrib.auth.models import User

from components.makahiki_profiles.models import Profile
  
class FacebookForm(forms.Form):
  can_post = forms.BooleanField(
        required=False, 
        initial=True,
        label="%s can post to my Facebook feed (at most 2 posts per day)" % settings.COMPETITION_NAME
  )

class ReferralForm(forms.Form):
  referrer_email = forms.EmailField(
        required=False,
        label='Referrer Email (Optional)'
  )
  
  def __init__(self, *args, **kwargs):  
    self.user = kwargs.pop('user', None)
      
    super(ReferralForm, self).__init__(*args, **kwargs)
    
  def clean(self):
    """
    Check if the user is not submitting their own email.
    """
    cleaned_data = self.cleaned_data
    if self.user.email == cleaned_data.get('referrer_email'):
      raise forms.ValidationError("Please use another user's email address, not your own.")
      
    return cleaned_data
    
  def clean_referrer_email(self):
    """
    Check if the user is a part of the competition.
    """
    email = self.cleaned_data['referrer_email']
    if email:
      # Check if user is in the system.
      try:
        user = User.objects.get(email=email, is_staff=False)
      except User.DoesNotExist:
        raise forms.ValidationError("Sorry, but that user is not a part of the competition.")
    return email
  
class ProfileForm(forms.Form):
  display_name = forms.CharField(
        max_length=20, 
        help_text="This name will be shown in scoreboards and on your profile instead of your UH username."
  )
  facebook_photo = forms.URLField(widget=forms.HiddenInput, required=False)
  use_fb_photo = forms.BooleanField(required=False)
  avatar = forms.ImageField(required=False)
  
  def __init__(self, *args, **kwargs):  
    """
    Override for init to take a user argument.
    """
    self.user = kwargs.pop('user', None)  
    super(ProfileForm, self).__init__(*args, **kwargs)
  
  def clean_display_name(self):
    name = self.cleaned_data['display_name'].strip()
    # Remove extra whitespace from the name.
    spaces = re.compile(r'\s+')
    name = spaces.sub(' ', name)
    
    # Check for name that is just whitespace.
    if name == '':
      raise forms.ValidationError('This field is required')
      
    # Check for duplicate name
    if Profile.objects.exclude(user=self.user).filter(name=name).count() > 0:
      raise forms.ValidationError("%s is taken.  Please use another name.")
      
    return name