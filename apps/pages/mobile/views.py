from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404

from components.activities.models import ActivityBase
from components.makahiki_base import get_current_round
from pages.view_activities.forms import *
from components.activities.models import *
from components.activities import * 
from components.makahiki_profiles.models import *
from components.makahiki_profiles import *
from datetime import timedelta, date
from time import strftime
from string import lower
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
 
def events(request,option): 
  eventlist = []
  user = request.user
  options = ["upcoming","attending","past"] 
  view = option

  #handle the date functionality
  day = timedelta(days = 1)
  today= datetime.date(2011,05,02)
  datelist = []
  #uncomment the below line to bring things up to date
  #today = date.today()
  datelist.append([])
  datelist[0].append(today)
  datelist[0].append(today.strftime("%A, %B %d"))
  temp = today
  for i in range(1,7,1):
    datelist.append([])
    temp += day
    datelist[i].append(temp)
    datelist[i].append(temp.strftime("%A, %B %d"))

  #upcoming
  if string.lower(option) == options[0] :
    eventlist = get_available_events(user)

  #attending
  elif string.lower(option) == options[1]:
    avail = get_available_events(user)  
    try:
      for event in avail:
        member = ActivityMember.objects.get(user=request.user,activity=event)
        if member.approval_status == "pending":
          eventlist.append(event) 
    except ActivityMember.DoesNotExist: 
      eventlist = ' '
  #past
  elif string.lower(option) == options[2]:   
    avail = get_available_events(user)
    for event in avail:
      if event.event_date.date() < today:
        eventlist.append(event)

  return render_to_response("mobile/events/index.html", {
  "view": view,
  "eventlist": eventlist,
  "options": options,
  "datelist": datelist,
  }, context_instance=RequestContext(request))
