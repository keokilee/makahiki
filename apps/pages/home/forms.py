from django import forms
from django.conf import settings

from components.makahiki_profiles.models import Profile
  
class FacebookForm(forms.Form):
  can_post = forms.BooleanField(
        required=False, 
        initial=True,
        label="%s can post to my Facebook feed (at most 2 posts per day)" % settings.COMPETITION_NAME
  )

class ProfileForm(forms.Form):
  display_name = forms.CharField(
        max_length=20, 
        help_text="This name will be shown in scoreboards and on your profile instead of your UH username."
  )
  facebook_photo = forms.URLField(widget=forms.HiddenInput, required=False)
  use_fb_photo = forms.BooleanField(required=False)
  avatar = forms.ImageField(required=False)
  
  def clean_display_name(self):
    """
    Validates the display name of the user.
    
    This needs to be implemented since some DBs (SQLite) do not have the ability to add unique constraints.
    """
    data = self.cleaned_data['display_name']
    try:
      profile = Profile.objects.get(name=data)
      raise forms.ValidationError("'%s' is taken, please enter another name." % data)
    except Profile.DoesNotExist:
      pass
      
    return data