from django.conf import settings
from django.http import HttpResponseRedirect
from components.makahiki_themes.forms import ThemeSelect

def change_theme(request):
  """Change the current theme."""
  if request.method == "POST":
    form = ThemeSelect(request.POST)
    if form.is_valid():
      settings.MAKAHIKI_THEME = form.cleaned_data["css_theme"]
  
  next = request.META.get("HTTP_REFERER", "/")
  return HttpResponseRedirect(next)
