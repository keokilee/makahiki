from django import forms
  
class WallForm(forms.Form):
  post = forms.CharField(widget=forms.Textarea(attrs={'cols': '60', 'rows': '2'}))