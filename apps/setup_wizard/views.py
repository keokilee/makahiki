from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from makahiki_facebook.models import FacebookProfile

import makahiki_facebook.facebook as fb
from setup_wizard.forms import TermsForm

def terms(request):
  """Display the terms and conditions."""
  if request.method == "POST":
    form = TermsForm(request.POST)
    # Form will probably be valid, but doesn't hurt to check.
    if form.is_valid(): 
      profile = request.user.get_profile()
      profile.data_opt_in = form.cleaned_data["accept"]
      profile.save()
      return HttpResponseRedirect(reverse("setup_facebook"))
    
  opt_out_form = TermsForm(initial={"accept": False})
  opt_in_form = TermsForm(initial={"accept": True})
  return render_to_response("setup_wizard/terms.html", {
    "opt_out_form": opt_out_form,
    "opt_in_form": opt_in_form,
  }, context_instance=RequestContext(request))
  
def facebook(request):
  """Ask the user if they'd like to use Facebook Connect."""
  return render_to_response("setup_wizard/facebook.html", {}, context_instance=RequestContext(request))
  
def profile(request):
  """Set up the user profile and use information from Facebook if available."""
  fb_user = fb.get_user_from_cookie(request.COOKIES, settings.FACEBOOK_APP_ID, settings.FACEBOOK_SECRET_KEY)
  if fb_user:
    fb_profile = FacebookProfile.create_or_update_from_fb_user(request.user, fb_user)
  return render_to_response("setup_wizard/profile.html", {}, context_instance=RequestContext(request))
  
def logout(request):
  """Logs out the user if they cancel at any point."""
  logout(request)
  return HttpResponseRedirect("/")