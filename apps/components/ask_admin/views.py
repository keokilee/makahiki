import simplejson as json

from django.http import Http404, HttpResponse
from django.template.loader import render_to_string
from django.core.mail import mail_admins
from django.contrib.sites.models import Site
from django.conf import settings
from django.core.urlresolvers import reverse

from components.ask_admin.forms import FeedbackForm

def send_feedback(request):
  if request.method == "POST" and request.is_ajax():
    form = FeedbackForm(request.POST)
    if form.is_valid():
      html_message = render_to_string("email/ask_admin.html", {
          "user": request.user,
          "url": form.cleaned_data["url"],
          "question": form.cleaned_data["question"],
      })
      message = render_to_string("email/ask_admin.txt", {
          "user": request.user,
          "url": form.cleaned_data["url"],
          "question": form.cleaned_data["url"],
      })
      
      current_site = Site.objects.get(id=settings.SITE_ID)
      mail_admins("[%s] Message for admins" % current_site.domain,
          message, html_message=html_message)
          
      return HttpResponse(json.dumps({"success": True}), mimetype="application/json")
  
  raise Http404