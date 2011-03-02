from django import forms
  
class WallForm(forms.Form):
  post = forms.CharField(widget=forms.Textarea, initial="What's on your mind?")
