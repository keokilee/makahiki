from django import forms
from django.contrib.auth import authenticate, login

class LoginForm(forms.Form):
    
    username = forms.CharField(label="Username", max_length=30, widget=forms.TextInput())
    password = forms.CharField(label="Password", widget=forms.PasswordInput(render_value=False))
    remember = forms.BooleanField(label="Remember Me", help_text="If checked you will stay logged in for 3 weeks", required=False)
    
    user = None
    
    def clean(self):
        if self._errors:
            return
        user = authenticate(username=self.cleaned_data["username"], password=self.cleaned_data["password"])
        if user:
            if user.is_active:
                self.user = user
            else:
                raise forms.ValidationError("This account is currently inactive.")
        else:
            raise forms.ValidationError("The username and/or password you specified are not correct.")
        return self.cleaned_data
    
    def login(self, request):
        if self.is_valid():
            login(request, self.user)
            request.user.message_set.create(message="Successfully logged in as %(username)s." % {'username': self.user.username})
            if self.cleaned_data['remember']:
                request.session.set_expiry(60 * 60 * 24 * 7 * 3)
            else:
                request.session.set_expiry(0)
            return True
        return False