import simplejson as json
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse

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
  """
  Shows a help topic.  This method handles both a regular request and an AJAX request for dialog boxes.
  """
  topic = get_object_or_404(HelpTopic, slug=slug, category=category)
  if request.is_ajax():
    contents = render_to_string("help/dialog.html", {"topic": topic})
    return HttpResponse(json.dumps({
        "title": topic.title,
        "contents": contents,
    }), mimetype="application/json")
    
  return render_to_response("help/topic.html", {
      "topic": topic,
  }, context_instance=RequestContext(request))
  

