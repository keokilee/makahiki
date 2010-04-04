from django import forms

class ThemeSelect(forms.Form):
  css_theme = forms.CharField(max_length=20)