from django.contrib.auth import SESSION_KEY
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect

@user_passes_test(lambda u: u.is_staff, login_url="/account/cas/login")
def login_as(request, user_id):
  """Admin method for logging in as another user."""
  # Solution found at http://copiousfreetime.blogspot.com/2006/12/django-su.html
  user = get_object_or_404(User, id=user_id)
  if user.is_active:
    request.session[SESSION_KEY] = user_id
    request.session['staff'] = True
    request.session.set_expiry(0) # Expire this session when the browser closes.
  return HttpResponseRedirect("/")