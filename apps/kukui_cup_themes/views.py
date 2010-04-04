# Create your views here.
import os

from django.conf import settings
from django.http import HttpResponseRedirect
from kukui_cup_themes.forms import ThemeSelect

def change_theme(request):
  """Change the current theme."""
  if request.method == "POST":
    form = ThemeSelect(request.POST)
    if form.is_valid():
      settings.KUKUI_CSS_THEME = form.cleaned_data["css_theme"]
      
  return HttpResponseRedirect("/")
  