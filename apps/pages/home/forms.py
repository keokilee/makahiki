from django import forms
from django.conf import settings
  
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
  about = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"cols": '50', 'rows': '2'}),
        label="""
              (Optional) What would you like other players of the %s to know about you (for your profile)?
              """ % settings.COMPETITION_NAME,
  )
