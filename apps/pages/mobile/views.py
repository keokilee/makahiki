from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404

from components.activities.models import ActivityBase

def index(request):
  return render_to_response("mobile/index.html", {}, context_instance=RequestContext(request))

def smartgrid(request):
  activities = ActivityBase.objects.order_by("category__name")

  return render_to_response("mobile/smartgrid/index.html", {
    "activities": activities,
  }, context_instance=RequestContext(request))

def task(request, activity_id):
  activity = get_object_or_404(ActivityBase, id=activity_id)

  return render_to_response("mobile/smartgrid/task.html", {
    "activity": activity,
  }, context_instance=RequestContext(request))

def sgresponse(request, activity_id):
  return render_to_response("mobile/smartgrid/response.html",{}, context_instance=RequestContext(request))

def landing(request):
  return render_to_response("mobile/landing.html", {}, context_instance=RequestContext(request))

def sevent(request):
  return render_to_response("mobile/events/sevent/index.html", {}, context_instance=RequestContext(request))

def events(request):
  return render_to_response("mobile/events/index.html", {}, context_instance=RequestContext(request))
