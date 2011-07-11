from django import forms
  
class WallForm(forms.Form):
  post = forms.CharField(widget=forms.Textarea, initial="Share something with the canopy.")
