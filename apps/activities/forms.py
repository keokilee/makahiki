from django import forms

class ActivityTextForm(forms.Form):
  response = forms.CharField(max_length=255)
  comment = forms.CharField(widget=forms.Textarea, required=False)
  question = forms.IntegerField(widget=forms.HiddenInput(), required=False)
  
class ActivityImageForm(forms.Form):
  image_response = forms.ImageField()
  comment = forms.CharField(widget=forms.Textarea, required=False)