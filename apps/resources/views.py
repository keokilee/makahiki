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
  view_all = request.GET.has_key("view_all") and request.GET["view_all"]
  view_all_url = None
  
  if request.GET.has_key("topics"):
    topic_form = TopicSelectForm(request.GET)
    if topic_form.is_valid():
      topics = topic_form.cleaned_data["topics"]
      if view_all:
        resources = Resource.objects.filter(topics__pk__in=topics).distinct().order_by("-created_at")
      else:
        resources = Resource.objects.filter(topics__pk__in=topics).distinct().order_by("-created_at")[0:DEFAULT_NUM_RESOURCES]
      resource_count = Resource.objects.filter(topics__pk__in=topics).distinct().count()
  
  else:
    # We get here on first load
    topic_form = TopicSelectForm() # Note that all topics are selected by default.
    if view_all:
      resources = Resource.objects.order_by("-created_at")
    else:
      resources = Resource.objects.order_by("-created_at")[0:DEFAULT_NUM_RESOURCES]
    resource_count = Resource.objects.count()

  # Create the list header and view all link.
  list_title = "%d resources"
  if not view_all and resource_count > DEFAULT_NUM_RESOURCES:
    view_all_url = _construct_all_url(request)
    list_title = list_title % DEFAULT_NUM_RESOURCES
  else:
    list_title = list_title % resource_count
    
  return render_to_response('resources/index.html', {
    "topic_form": topic_form,
    "resources": resources,
    "list_title": list_title,
    "resource_count": resource_count,
    "view_all_url": view_all_url,
  }, context_instance = RequestContext(request))
  
def _construct_all_url(request):
  """Constructs a view all url using the parameters in the request."""
  url = request.get_full_path()
  all_param = "view_all=True"
  if request.GET.has_key("topics"):
    # If this url has topics, we append the view all parameter.
    url += "&view_all=True"
  else:
    # We need to create a GET parameter.
    url += "?view_all=True"
  
  return url
  
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