from django import forms

class ActivityTextForm(forms.Form):
  response = forms.CharField(max_length=255)
  comment = forms.CharField(widget=forms.Textarea)
  question = forms.HiddenInput()
  
class ActivityImageForm(forms.Form):
  image_response = forms.ImageField()
  comment = forms.CharField(widget=forms.Textarea)