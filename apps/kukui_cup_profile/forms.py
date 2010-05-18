from django.conf import settings
from django import forms

from kukui_cup_profile.models import Profile

class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        exclude = ('user', 'points', 'floor')
