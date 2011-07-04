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
from django.contrib.auth.decorators import login_required
from components.quests.models import *
from components.quests import *

def index(request):
  return render_to_response("mobile/index.html", {}, context_instance=RequestContext(request))

@login_required
def smartgrid(request):
  activities = ActivityBase.objects.order_by("priority")

  return render_to_response("mobile/smartgrid/index.html", {
    "activities": activities,
  }, context_instance=RequestContext(request))

@login_required
def basicenrg(request):
  activities = ActivityBase.objects.order_by("priority")
  return render_to_response("mobile/smartgrid/basicenrg.html", {
    "activities": activities,
  }, context_instance=RequestContext(request))

@login_required
def getstarted(request):
  activities = ActivityBase.objects.order_by("priority")
  return render_to_response("mobile/smartgrid/getstarted.html", {
    "activities": activities,
  }, context_instance=RequestContext(request))

@login_required
def movingon(request):
  activities = ActivityBase.objects.order_by("priority")
  return render_to_response("mobile/smartgrid/movingon.html", {
    "activities": activities,
  }, context_instance=RequestContext(request))

@login_required
def lightsout(request):
  activities = ActivityBase.objects.order_by("priority")
  return render_to_response("mobile/smartgrid/lightsout.html", {
    "activities": activities,
  }, context_instance=RequestContext(request))

@login_required
def makewatts(request):
  activities = ActivityBase.objects.order_by("priority")
  return render_to_response("mobile/smartgrid/makewatts.html", {
    "activities": activities,
  }, context_instance=RequestContext(request))

@login_required
def potpourri(request):
  activities = ActivityBase.objects.order_by("priority")
  return render_to_response("mobile/smartgrid/potpourri.html", {
    "activities": activities,
  }, context_instance=RequestContext(request))

@login_required
def opala(request):
  activities = ActivityBase.objects.order_by("priority")
  return render_to_response("mobile/smartgrid/opala.html", {
    "activities": activities,
  }, context_instance=RequestContext(request))

@login_required
def task(request, activity_id):
  activity = get_object_or_404(ActivityBase, id=activity_id)

  return render_to_response("mobile/smartgrid/task.html", {
    "activity": activity,
  }, context_instance=RequestContext(request))

@login_required
def sgform(request, activity_id):
  activity = get_object_or_404(ActivityBase, id=activity_id)

  return render_to_response("mobile/smartgrid/form.html", {
    "activity": activity,
  }, context_instance=RequestContext(request))

def landing(request):
  return render_to_response("mobile/landing.html", {}, context_instance=RequestContext(request))
 
class EventDay:
  def __init__(self):
    self.date = ''
    self.datestring = ''
    self.eventlist = []
    self.count = 0
  def __str__(self):
    return "obj= " + str(self.date) + " " +  " " + str(self.eventlist)

@login_required
def events(request,option): 
  objlist = []
  user = request.user
  options = ["upcoming","attending","past"] 
  view = option

  #handle the date functionality
  day = timedelta(days = 1)
  #today= datetime.date(2011,05,20)
  today= datetime.date(2011,05,03)
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
    events = get_available_events(user) 
    for element in datelist:
      obj = EventDay()
      obj.date = element[0]
      obj.datestring = element[1]
      temparray = [] 
      count = 0
      for event in events:
        aux = event.event_date.date
        if event.event_date.strftime("%B %d, %y") == obj.date.strftime("%B %d, %y"):
          temparray.append(event)
          count = count + 1 
      obj.count = count
      obj.eventlist = temparray
      objlist.append(obj)
  #attending
  elif string.lower(option) == options[1]:
    avail = get_available_events(user)  
    attending = []
    try:
      for event in avail:
        member = ActivityMember.objects.get(user=request.user,activity=event)
        if member.approval_status == "pending":
          attending.append(event) 
    except ActivityMember.DoesNotExist: 
          boolean = False
    for element in datelist:
      obj = EventDay()
      obj.date = element[0]
      obj.datestring = element[1]
      count = 0
      temparray = [] 
      for event in attending: 
        if event.event_date.strftime("%B %d, %y") == obj.date.strftime("%B %d, %y"):
          temparray.append(event)
          count = count + 1 
      obj.count = count
      obj.eventlist = temparray
      objlist.append(obj)
  

  #past
  elif string.lower(option) == options[2]:   
    avail = get_available_events(user)
    for event in avail:
      if event.event_date.date() < today:
        objlist.append(event)

  return render_to_response("mobile/events/index.html", {
  "view": view, 
  "objlist": objlist,
  "options": options, 
  }, context_instance=RequestContext(request))



@login_required
def quests(request,option): 
  questlist = []
  user = request.user
  options = ["available","accepted","completed"] 
  view = option 

  #completed
  if string.lower(option) == options[2]:
    questlist = Quest.objects.filter(questmember__user=request.user,questmember__completed=True)  

  return render_to_response("mobile/quests/index.html", {
  "view": view,
  "questlist": questlist,
  "options": options, 
  }, context_instance=RequestContext(request))

@login_required
def quest_detail(request, slug):
  quest=get_object_or_404(Quest,quest_slug=slug)  
  return render_to_response("mobile/quests/details.html", {
    "quest": quest,
  }, context_instance=RequestContext(request))
