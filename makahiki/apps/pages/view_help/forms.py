from django import forms

class AskAdminForm(forms.Form):
  question = forms.CharField(required=False, widget=forms.Textarea())


  
