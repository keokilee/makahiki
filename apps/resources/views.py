import string

from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404

from resources import DEFAULT_NUM_RESOURCES
from resources.models import Resource, Topic
from resources.forms import TopicSelectForm
# Create your views here.

def index(request):
  """Index page for the resources tab."""
  resources = None
  resource_count = 0
  topics = None
  list_title = "All Resources"
  
  if request.method == "POST":
    form = TopicSelectForm(request.POST)
    if form.is_valid():
      topics = form.cleaned_data["topics"]
      if len(topics) == 0:
        resources = Resource.objects.order_by("-created_at")[0:DEFAULT_NUM_RESOURCES]
      else:
        resources = Resource.objects.filter(topics__pk__in=topics).distinct().order_by("-created_at")[0:DEFAULT_NUM_RESOURCES]
        resource_count = Resource.objects.filter(topics__pk__in=topics).distinct().order_by("-created_at").count()
          
  if topics and resources:
    form = TopicSelectForm(initial={"topics": [topic.pk for topic in topics]})
    list_title = "Resources in %s" % string.join([topic.topic for topic in topics], ", ")
  else:
    form = TopicSelectForm()
    resources = Resource.objects.order_by("-created_at")[0:DEFAULT_NUM_RESOURCES]
    resource_count = Resource.objects.count()
    
  more_resources = False
  if resource_count > DEFAULT_NUM_RESOURCES:
    more_resources = True
    
  return render_to_response('resources/index.html', {
    "topic_form": form,
    "resources": resources,
    "more": more_resources,
    "list_title": list_title,
  }, context_instance = RequestContext(request))
  
def topic(request, topic_id):
  """View resources for a given topic."""
  topic = get_object_or_404(Topic, pk=topic_id)
  resources = topic.resource_set.all()
  return render_to_response('resources/list.html', {
    "topic": topic.topic,
    "resources": resources,
  }, context_instance = RequestContext(request))
  
def media(request, media_type):
  """View resources for a given media type."""
  type_string = None
  for media in Resource.MEDIA_TYPES:
     if media_type == media[0]:
       type_string = media[1]
       break
  if not type_string: 
    raise Http404
  
  resources = Resource.objects.filter(
    media_type=type_string
  )
  
  return render_to_response('resources/list.html', {
    "media": type_string,
    "resources": resources,
  }, context_instance = RequestContext(request))
  
def resource(request, resource_id):
  """View details for a resource."""
  resource = get_object_or_404(Resource, pk=resource_id)
  
  return render_to_response('resources/resource_detail.html', {
    "resource": resource,
  }, context_instance = RequestContext(request))