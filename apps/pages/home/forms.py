from django import forms
from django.conf import settings
from django.contrib.auth.models import User
  
class FacebookForm(forms.Form):
  can_post = forms.BooleanField(
        required=False, 
        initial=True,
        label="%s can post to my Facebook feed (at most 2 posts per day)" % settings.COMPETITION_NAME
  )

class ReferralForm(forms.Form):
  referrer_email = forms.EmailField(
        required=False,
        help_text="If someone has referred you to the Kukui Cup, enter their UH email here.  " + \
                  "If you get at least 30 points, both you and the person who referred you will get an additional 10 points!"
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
        user = User.objects.get(email=email)
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
  
  # def clean_display_name(self):
  #     """
  #     Validates the display name of the user.
  #     
  #     This needs to be implemented since some DBs (SQLite) do not have the ability to add unique constraints.
  #     """
  #     data = self.cleaned_data['display_name']
  #     try:
  #       profile = Profile.objects.get(name=data.strip())
  #       raise forms.ValidationError("'%s' is taken, please enter another name." % data)
  #     except Profile.DoesNotExist:
  #       pass
  #       
  #     return data