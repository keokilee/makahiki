from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from components.help_topics.models import HelpTopic
from components.ask_admin.forms import FeedbackForm

@login_required
def index(request):
  form = FeedbackForm(auto_id="help_%s")
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

