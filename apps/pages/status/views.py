# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User

from components.makahiki_profiles.models import Profile
from components.prizes.models import RafflePrize


@user_passes_test(lambda u: u.is_staff, login_url="/account/cas/login")
def status(request):
  return render_to_response("admin/status.html", {}, context_instance=RequestContext(request))