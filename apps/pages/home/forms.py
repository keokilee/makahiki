from django import forms
from django.conf import settings
  
class FacebookForm(forms.Form):
  can_post = forms.BooleanField(
        required=False, 
        label="%s can post to my Facebook feed (at most 2 posts per day)" % settings.COMPETITION_NAME
  )

class ProfileForm(forms.Form):
  display_name = forms.CharField(max_length=12)
  about = forms.CharField(widget=forms.Textarea(attrs={"cols": '50', 'rows': '2'}))