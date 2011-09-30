# Create your views here.
import datetime

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.conf import settings

from components.activities import get_popular_activities, get_popular_commitments
from components.activities.models import ActivityBase
from components.floors.models import Floor
from components.makahiki_base import get_current_round
from components.makahiki_profiles.models import Profile, ScoreboardEntry
from components.prizes.models import RaffleDeadline


@user_passes_test(lambda u: u.is_staff, login_url="/account/cas/login")
def home(request):
  return render_to_response("status/home.html", {}, context_instance=RequestContext(request))
  
@user_passes_test(lambda u: u.is_staff, login_url="/account/cas/login")
def points_scoreboard(request):
  profiles = Profile.objects.filter(
    points__gt=0,
  ).order_by("-points", "-last_awarded_submission").values("name", "points")
  
  floor_standings = Floor.floor_points_leaders(num_results=10)
  
  round_individuals = {}
  round_floors = {}
  for round_name in settings.COMPETITION_ROUNDS:
    round_individuals[round_name] = ScoreboardEntry.objects.filter(
        points__gt=0,
    ).order_by("-points", "-last_awarded_submission").values("profile__name", "points")
    
    round_floors[round_name] = Floor.floor_points_leaders(
        num_results=10, 
        round_name=round_name
    )
    
  return render_to_response("status/points.html", {
      "profiles": profiles,
      "round_individuals": round_individuals,
      "floor_standings": floor_standings,
      "round_floors": round_floors,
  }, context_instance=RequestContext(request))
  
@user_passes_test(lambda u: u.is_staff, login_url="/account/cas/login")
def energy_scoreboard(request):
  return render_to_response("status/energy.html", {}, context_instance=RequestContext(request))
    
@user_passes_test(lambda u: u.is_staff, login_url="/account/cas/login")
def users(request):
  users = User.objects.filter(profile__last_visit_date=datetime.datetime.today())
  return render_to_response("status/users.html", {
      "users": users,
  }, context_instance=RequestContext(request))

@user_passes_test(lambda u: u.is_staff, login_url="/account/cas/login")
def prizes(request):
  deadlines = RaffleDeadline.objects.all().order_by("pub_date")
  return render_to_response("status/prizes.html", {
      "deadlines": deadlines,
  }, context_instance=RequestContext(request))
    
@user_passes_test(lambda u: u.is_staff, login_url="/account/cas/login")
def popular_activities(request):
  tasks = {}
  types = ActivityBase.objects.values('type').distinct()
  for item in types:
    task_type = item["type"]
    if task_type == 'commitment':
      tasks[task_type] = get_popular_commitments()
    else:
      tasks[task_type] = get_popular_activities(activity_type=task_type)
  
  return render_to_response("status/activities.html", {
      "tasks": tasks,
  }, context_instance=RequestContext(request))
        
@user_passes_test(lambda u: u.is_staff, login_url="/account/cas/login")
def event_rsvps(request):
  return render_to_response("status/rsvps.html", {}, context_instance=RequestContext(request))
  
  