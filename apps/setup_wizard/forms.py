from django import forms

class TermsForm(forms.Form):
  # Seems that required means that the value must be True.
  accept = forms.BooleanField(widget=forms.HiddenInput(), required=False)
