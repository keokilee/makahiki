from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.conf import settings
from django.views.decorators.cache import never_cache

from pages.landing.forms import LoginForm

@never_cache
def index(request):
  if request.mobile and not request.COOKIES.has_key("mobile-desktop"):
    return HttpResponseRedirect(reverse("mobile_landing"))
    # return HttpResponseRedirect(reverse("mobile_temp"))
  elif request.user.is_authenticated():
    return HttpResponseRedirect(reverse("home_index"))
  elif hasattr(settings, "ROOT_REDIRECT_URL") and settings.ROOT_REDIRECT_URL:
    return HttpResponseRedirect(settings.ROOT_REDIRECT_URL)
    
  return landing(request)
  
def landing(request):
  return render_to_response("landing/index.html", {}, context_instance=RequestContext(request))
  
def about(request):
  return render_to_response("landing/about.html", {}, context_instance=RequestContext(request))  
  
def login(request, form_class=LoginForm, template_name="account/login.html",
        success_url=None, url_required=False, extra_context=None):
  if extra_context is None:
      extra_context = {}
  if success_url is None:
      success_url = '/home'
  if request.method == "POST" and not url_required:
      form = form_class(request.POST)
      if form.login(request):
          return HttpResponseRedirect(success_url)
  else:
      form = form_class()
  ctx = {
      "form": form,
      "url_required": url_required,
  }
  ctx.update(extra_context)
  return render_to_response(template_name, ctx,
      context_instance = RequestContext(request)
  )