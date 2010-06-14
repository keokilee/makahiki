from django.conf import settings
from django import forms

from makahiki_profiles.models import Profile

class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        exclude = ('user', 'points', 'floor')
