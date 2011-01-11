from django import forms
  
class WallForm(forms.Form):
  post = forms.CharField()