import os

from django import forms
from django.conf import settings

def _get_installed_themes():
  """Get a list of installed themes to be shown in the select widget."""
  theme_dir = os.path.join(settings.PROJECT_ROOT, "media/css")
  return ((item, item) for item in os.listdir(theme_dir) if os.path.isdir(os.path.join(theme_dir, item)))
      
class ThemeSelect(forms.Form):
  """Form for selecting the installed theme."""
  css_theme = forms.ChoiceField(choices=_get_installed_themes())