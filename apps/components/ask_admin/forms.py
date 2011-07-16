from django import forms

class FeedbackForm(forms.Form):
  url = forms.URLField(required=False)
  question = forms.CharField(widget=forms.Textarea())
