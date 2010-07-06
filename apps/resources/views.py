from django.template import RequestContext
from resources.models import Resource, Topic
from django.shortcuts import render_to_response, get_object_or_404
# Create your views here.

def index(request):
  """Index page for the resources tab."""
  topics = Topic.objects.all()
  resources = Resource.objects.order_by("-created_at")
  media_types = set([resource.media_type for resource in resources])
  return render_to_response('resources/index.html', {
    "topics": topics,
    "media_types": media_types,
    "new_resources": resources[0:10],
  }, context_instance = RequestContext(request))
  
def topic(request, topic_id):
  """View resources for a given topic."""
  topic = get_object_or_404(Topic, pk=topic_id)
  resources = topic.resource_set.all()
  
  return render_to_response('resources/topic.html', {
    "topic": topic,
    "resources": resources,
  }, context_instance = RequestContext(request))
  
def resource(request, resource_id):
  """View details for a resource."""
  resource = get_object_or_404(Resource, pk=resource_id)
  
  return render_to_response('resources/resource_detail.html', {
    "resource": resource,
  }, context_instance = RequestContext(request))