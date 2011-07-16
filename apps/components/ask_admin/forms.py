from django import forms

class FeedbackForm(forms.Form):
  url = forms.URLField(required=False, widget=forms.HiddenInput)
  question = forms.CharField(widget=forms.Textarea())
