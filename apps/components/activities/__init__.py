import datetime

from django.db.models import Q
from django.conf import settings
from components.activities.models import *
from django.db.models import Sum, Count
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User


# Directory in which to save image files for ActivityMember verification.
from apps.components.activities.models import Activity, ActivityMember, CommitmentMember

ACTIVITY_FILE_DIR = getattr(settings, 'ACTIVITY_FILE_DIR', 'activities')

# Maximum number of commitments user can have at one time.
MAX_COMMITMENTS = 5

def get_popular_tasks():
  """
  Returns a dictionary containing the most popular tasks.
  The keys are the type of the task and the values are a list of tasks.
  """
  return {
    "Activity": get_popular_activities("activity")[:5],
    "Commitment": get_popular_commitments()[:5],
    "Event": get_popular_activities("event")[:5],
    "Survey": get_popular_activities("survey")[:5],
    "Excursion": get_popular_activities("excursion")[:5],
  }
  
def get_popular_activities(activity_type="activity"):
  """Gets the most popular activities in terms of completions."""
  return Activity.objects.filter(
      activitymember__approval_status="approved",
      type=activity_type,
  ).values("title", "type", "slug").annotate(completions=Count("activitymember")).order_by("-completions")
  
def get_popular_commitments():
  """Gets the most popular commitments in terms of completions."""
  return Commitment.objects.filter(
      commitmentmember__award_date__isnull=False,
  ).values("title", "type", "slug").annotate(completions=Count("commitmentmember")).order_by("-completions")

def get_incomplete_tasks(user):
  """Gets user's incomplete activities and commitments. Returns a dictionary."""
  
  user_commitments = get_current_commitments(user)
  user_activities = get_current_activities(user)
    
  return {
    "commitments": user_commitments,
    "activities": user_activities,
  }
  
def get_incomplete_task_members(user):
  """Gets user's incomplete activity and commitment members."""
  commitment_members = get_current_commitment_members(user)
  activity_members = get_current_activity_members(user)
  
  return {
    "commitments": commitment_members,
    "activities": activity_members,
  }
  
def can_add_commitments(user):
  """Determines if the user can add additional commitments."""
  return get_current_commitments(user).count() < MAX_COMMITMENTS
  
def get_current_commitments(user):
  """Get the user's incomplete commitments."""
  return user.commitment_set.filter(
    commitmentmember__award_date=None,
  ).order_by("commitmentmember__completion_date")
  
def get_current_commitment_members(user):
  """Get the user's membership objects in the incomplete commitments."""
  return user.commitmentmember_set.filter(
    award_date=None
  ).order_by("completion_date")
  
def get_available_commitments(user):
  """Get any commitments that the user is not currently active in."""
  return Commitment.objects.exclude(
    id__in=get_current_commitments(user),
  ).order_by("title")

def get_completed_commitments(user):
  """Gets the user's completed commitments"""
  return user.commitment_set.filter(
    commitmentmember__award_date__isnull=False,
  ).order_by("title")
  
def get_current_activities(user):
  """Get the user's incomplete activities."""
  
  return user.activity_set.filter(
    activitymember__award_date=None,
  ).order_by("activitymember__submission_date")
  
def get_current_activity_members(user):
  """Get the user's incomplete activity members."""
  return user.activitymember_set.exclude(
    activity__type="survey",
  ).filter(
    award_date=None,
  ).order_by("submission_date")
  
def get_available_activities(user):
  """Retrieves only the activities that a user can participate in (excluding events)."""
  
  activities = Activity.objects.exclude(
    activitymember__user=user,
  ).filter(
    type='activity',
    pub_date__lte=datetime.date.today(),
    expire_date__gte=datetime.date.today(),
  ).order_by("priority", "title")
  
  return activities

def get_available_golow_activities(user):
  """Retrieves only the golow activities that a user can participate in (excluding events)."""
  
  activities = Activity.objects.exclude(
    activitymember__user=user,
  ).filter(
    energy_related=True,
    pub_date__lte=datetime.date.today(),
    expire_date__gte=datetime.date.today(),    
  ).order_by("type", "priority")
  
  commitments = Commitment.objects.exclude(
    commitmentmember__user=user,
  ).filter(
    energy_related=True,
  ).order_by("type", "priority")
  
  golow_tasks = []
  for task in commitments:
    if is_unlock(user, task):
      golow_tasks.append(task)
      break
          
  _pick_one_activity_per_type(user, activities, golow_tasks)
  
  if len(golow_tasks) < 3:
    _pick_one_activity_per_type(user, activities, golow_tasks)
    
  return golow_tasks

def _pick_one_activity_per_type(user, activities, golow_tasks):
  type = None
  for task in activities:
    if task in golow_tasks:
      continue;
      
    if type == task.type:
      continue
    
    if is_unlock(user, task):
      golow_tasks.append(task)
      type = task.type
        
      if len(golow_tasks) == 3:
        break
  
def get_available_events(user):
  """Retrieves only the events that a user can participate in."""

  events = Activity.objects.filter(
    Q(type='event')|Q(type='excursion'),
    pub_date__lte=datetime.date.today(),
    expire_date__gte=datetime.date.today(),
    event_date__gte=datetime.date.today(),
    is_canopy=False,
  ).order_by("event_date","priority")

  unlock_events = []
  for event in events:
    if is_unlock(user, event):
      unlock_events.append(event)

  return unlock_events # Filters out inactive activities.
  
def get_completed_activities(user):
  """Gets the user's completed activities"""
  return user.activity_set.filter(
    activitymember__award_date__isnull=False,
  ).order_by("title")

def get_completed_tasks(user, category):
  """Gets the user's completed tasks by category"""
  return Activity.objects.filter(activitymember__user=user, category=category).count() + Commitment.objects.filter(commitmentmember__user=user,category=category).count()
         
def get_awarded_points(user, category):
  """Gets the user's awarded points by category"""
  asum = Activity.objects.filter(activitymember__user=user, category=category).aggregate(Sum('point_value'))
  apoint = asum['point_value__sum']
  if apoint == None:
    apoint = 0;
  csum = Commitment.objects.filter(commitmentmember__user=user,category=category).aggregate(Sum('point_value'))
  cpoint = csum['point_value__sum']
  if cpoint == None:
    cpoint = 0;
  return 0 + apoint + cpoint

def is_pau(user, task):
  return is_pau_by_id(user, task.id, task.type)

def is_pau_by_id(user, task_id, task_type):
  if task_type != "commitment":
    is_pau = ActivityMember.objects.filter(user=user, activity__id=task_id).count() > 0
  else:
    is_pau = CommitmentMember.objects.filter(user=user, commitment__id=task_id).count() > 0
  return is_pau

def completedAllOf(user, cat_slug):
  """completed all of the category"""
  try:
    cat = Category.objects.get(slug=cat_slug)
  except ObjectDoesNotExist:
      return False  

  for task in cat.activitybase_set.all():
    if is_pau(user, task) != True:
      return False
  
  return True

def completedSomeOf(user, some, cat_slug):
  """completed some of the category"""
  try:
    cat = Category.objects.get(slug=cat_slug)
  except ObjectDoesNotExist: 
      return False
      
  count = 0
  for task in cat.activitybase_set.all():
    if is_pau(user, task):
      count = count + 1
    if count == some:
      return True
    
  return False  
    
def completed(user, activity_members, commitment_members, task_slug):
  """completed the task"""

  if activity_members != None:
      for member in activity_members:
          if member["slug"] == task_slug:
              return True

      for member in commitment_members:
          if member["slug"] == task_slug:
              return True
  else:
      try:
        task = ActivityBase.objects.get(slug=task_slug)
      except ObjectDoesNotExist:
          return False

      return is_pau(user, task)

def afterPublished(task_id):
  """return true if the event/excursion have been published"""
  try:
    return Activity.get(id=task_id).pub_date <= datetime.date.today()
  except:
    return False
    
def is_unlock(user, task):
  """determine the unlock status of a task by dependency expression"""

  # only canopy member able to see canopy activity
  try:
    profile = self.user.get_profile()
  except:
    profile = None

  if task.is_canopy and profile != None and not profile.canopy_member:
     return False;

  return is_unlock_by_id(user, task.id, task.depends_on, None, None)

def is_unlock_by_id(user, task_id, task_depends_on, activity_members, commitment_members):
  expr = task_depends_on
  if expr == None or expr == "":
    return False
  
  expr = expr.replace("completedAllOf(", "completedAllOf(user,")
  expr = expr.replace("completedSomeOf(", "completedSomeOf(user,")
  expr = expr.replace("completed(", "completed(user,activity_members,commitment_members,")
  expr = expr.replace("afterPublished(", "afterPublished(%d" % (task_id))

  allow_dict = {'completedAllOf':completedAllOf,
                'completedSomeOf':completedSomeOf, 
                'completed':completed,
                'afterPublished':afterPublished,
                'True':True,
                'False':False,
                'user':user,
                'activity_members':activity_members,
                'commitment_members':commitment_members,
               }

  return eval(expr, {"__builtins__":None}, allow_dict)
  
def annotate_task_status(user, task):
  """Adds additional fields that identify whether or not the activity is approved."""

  if task.type == "event" or task.type == "excursion":
    task.is_event_pau = task.activity.is_event_completed()

  task.is_pau = is_pau(user, task)
  if task.is_pau:
      task.is_unlock = True
      if task.type != "commitment":
        members = ActivityMember.objects.filter(user=user, activity=task).order_by("-updated_at").values("approval_status","award_date")
      else:
        members = CommitmentMember.objects.filter(user=user, commitment=task).order_by("-updated_at").values("completion_date", "award_date")

      if members:
        task.approval = members[0]
        print task.approval
        if task.type == "commitment":
          task.approval["days_left"] = task.approval["completion_date"] - datetime.date.today()
  else:
    task.is_unlock = is_unlock(user, task)
      
  return task


def annotate_simple_task_status(user, task, activity_members, commitment_members):
  """Adds additional fields that identify whether or not the activity is approved."""

  has_member = None
  if task["type"] !="commitment":
      for member in activity_members:
        if member["activity_id"] == task["id"]:
            has_member = member
  else:
      for member in commitment_members:
        if member["commitment_id"] == task["id"]:
            has_member = member

  if has_member:
      task["is_pau"] = True
      task["is_unlock"] = True
      task["approval"] = has_member
      if task["type"] == "commitment":
          diff = task["approval"]["completion_date"] - datetime.date.today()
          if diff.days < 0:
            task["approval"]["days_left"] =  0
          else:
            task["approval"]["days_left"] =  diff.days

          commitment = Commitment.objects.filter(activitybase_ptr__id=task["id"]).values("point_value")[0]
          task["point_value"]=commitment["point_value"]
      else:
        activity = Activity.objects.filter(activitybase_ptr__id=task["id"]).values("event_date", "point_value", "point_range_start", "point_range_end")[0]
        task["point_value"]=activity["point_value"]
        task["point_range_start"]=activity["point_range_start"]
        task["point_range_end"]=activity["point_range_end"]
        if activity["event_date"]:
            result = datetime.datetime.today() - activity["event_date"]
            if result.days >= 0 and result.seconds >= 0:
              task["is_event_pau"] = True
            else:
              task["is_event_pau"] = False
  else:
    task["is_pau"] = False
    task["is_unlock"] = is_unlock_by_id(user, task["id"], task["depends_on"], activity_members, commitment_members)
    if task["is_unlock"]:
        if task["type"] == "commitment":
            commitment = Commitment.objects.filter(activitybase_ptr__id=task["id"]).values("point_value")[0]
            task["point_value"]=commitment["point_value"]
        else:
          activity = Activity.objects.filter(activitybase_ptr__id=task["id"]).values("event_date", "point_value", "point_range_start", "point_range_end")[0]
          task["point_value"]=activity["point_value"]
          task["point_range_start"]=activity["point_range_start"]
          task["point_range_end"]=activity["point_range_end"]

  return task

def get_user_by_email(email):
  """return the user from given email"""
  try:
    return User.objects.get(email=email);
  except ObjectDoesNotExist:
    return None

