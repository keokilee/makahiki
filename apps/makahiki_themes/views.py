import os

from django.conf import settings
from django.http import HttpResponseRedirect
from makahiki_themes.forms import ThemeSelect

def change_theme(request):
  """Change the current theme."""
  if request.method == "POST":
    form = ThemeSelect(request.POST)
    if form.is_valid():
      if request.user and request.user.is_authenticated():
        profile = request.user.get_profile()
        profile.theme = form.cleaned_data["css_theme"]
        profile.save()
      else:
        settings.KUKUI_CSS_THEME = form.cleaned_data["css_theme"]
      
  return HttpResponseRedirect("/")
