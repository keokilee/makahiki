from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from components.help_topics.models import HelpTopic
from pages.view_help.forms import AskAdminForm

@login_required
def index(request):
  form = None
  if request.method == "POST":
    form = AskAdminForm(request.POST)
    if form.is_valid():
      user = request.user
      email = user.get_profile().contact_email or user.email
      form.success = "Your question has been sent to the Kukui Cup administrators. We will email a response to " + email
      
  if not form:
    form = AskAdminForm()
    
  rules = HelpTopic.objects.filter(category="rules", parent_topic__isnull=True)
  faqs = HelpTopic.objects.filter(category="faq", parent_topic__isnull=True)
  return render_to_response("help/index.html", {
      "form": form,
      "rules": rules,
      "faqs": faqs,
  }, context_instance=RequestContext(request))

@login_required
def topic(request, category, slug):
  topic = get_object_or_404(HelpTopic, slug=slug, category=category)
  return render_to_response("help/topic.html", {
      "topic": topic,
  }, context_instance=RequestContext(request))

