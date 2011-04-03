from django import forms
  
class EnergyWallForm(forms.Form):
  post = forms.CharField(widget=forms.Textarea, initial="What's on your mind?")
