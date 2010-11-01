from django import forms

class TermsForm(forms.Form):
  # Seems that required means that the value must be True.
  accept = forms.BooleanField(widget=forms.HiddenInput(), required=False)

class ProfileForm(forms.Form):
  display_name = forms.CharField(max_length=12)
  about = forms.CharField(widget=forms.Textarea(attrs={"cols": '50', 'rows': '2'}))