import datetime

from django.db.models import Q
from django.conf import settings
from components.activities.models import *
from django.db.models import Sum, Count
from django.core.exceptions import ObjectDoesNotExist

# Directory in which to save image files for ActivityMember verification.
ACTIVITY_FILE_DIR = getattr(settings, 'ACTIVITY_FILE_DIR', 'activities')

# Maximum number of commitments user can have at one time.
MAX_COMMITMENTS = 5

def get_popular_tasks():
  """
  Returns a dictionary containing the most popular tasks.
  The keys are the type of the task and the values are a list of tasks.
  """
  # TODO: Make this more flexible once generic memberships are working.
  return {
    "Activity": get_popular_activities()[:5],
    "Commitment": get_popular_commitments()[:5],
    "Event": [],
    "Survey": [],
    "Excursion": [],
  }
  
def get_popular_activities():
  """Gets the most popular activities in terms of completions."""
  return Activity.objects.filter(
      activitymember__approval_status="approved",
  ).annotate(completions=Count("activitymember")).order_by("-completions")
  
def get_popular_commitments():
  """Gets the most popular commitments in terms of completions."""
  return Commitment.objects.filter(
      commitmentmember__award_date__isnull=False,
  ).annotate(completions=Count("commitmentmember")).order_by("-completions")

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
  return user.activitymember_set.filter(
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
  ).order_by("type","category", "priority")
  
  commitments = Commitment.objects.exclude(
    commitmentmember__user=user,
  ).filter(
    energy_related=True,
  ).order_by("type","category", "priority")
  
  golow_tasks = []
  count = 0
  type = None
  for task in commitments:
    if is_unlock(user, task):
      golow_tasks.append(task)
      count = count + 1
      break
      
  for task in activities:
    if type == task.type:
      continue
    
    if is_unlock(user, task):
      golow_tasks.append(task)
      count = count + 1
      type = task.type
    
    if count >= 3:
      break
    
  return golow_tasks
  
def get_available_events(user):
  """Retrieves only the events that a user can participate in."""

  events = Activity.objects.exclude(
    activitymember__user=user,
  ).filter(
    type='event',
    pub_date__lte=datetime.date.today(),
    expire_date__gte=datetime.date.today(),
  ).order_by("priority", "title")

  return events # Filters out inactive activities.
  
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
  if task.type != "commitment":
    is_pau = ActivityMember.objects.filter(user=user, activity__id=task.id).count() > 0
  else:
    is_pau = CommitmentMember.objects.filter(user=user, commitment__id=task.id).count() > 0  
  return is_pau

def completedAllOf(user, cat_name):
  """completed all of the category"""
  try:
    cat = Category.objects.get(name=cat_name)
    for task in cat.activitybase_set.all():
      if is_pau(user, task) != True:
        return False
  
    return True
  except ObjectDoesNotExist:
    return False

def completedSomeOf(user, some, cat_name):
  """completed some of the category"""
  try:
    cat = Category.objects.get(name=cat_name)
    count = 0
    for task in cat.activitybase_set.all():
      if is_pau(user, task):
        count = count + 1
      if count == some:
        return True
    
    return False
  except ObjectDoesNotExist:
    return False
    
def completed(user, task_name):
  """completed the task"""
  try:
    task = ActivityBase.objects.get(name=task_name)
    return is_pau(user, task)
  except ObjectDoesNotExist:
    return False

def afterPublished(task_name):
  """return true if the event/excursion have been published"""
  try:
    task = ActivityBase.objects.get(name=task_name)
    if task.type == "event" or task.type == "excursion":
      return task.activity.pub_date <= datetime.date.today()
      
    return False;  
  except ObjectDoesNotExist:
    return False 
  
def is_unlock(user, task):
  """determine the unlock status of a task by dependency expression"""
  expr = task.depends_on
  if expr == None or expr == "":
    return False
  
  expr = expr.replace("completedAllOf(", "completedAllOf(user,")
  expr = expr.replace("completedSomeOf(", "completedSomeOf(user,")
  expr = expr.replace("completed(", "completed(user,")
  expr = expr.replace("afterPublished(", "afterPublished('"+task.name+"'")

  allow_dict = {'completedAllOf':completedAllOf,
                'completedSomeOf':completedSomeOf, 
                'completed':completed,
                'afterPublished':afterPublished,
                'True':True,
                'False':False,
                'user':user,
               }

  return eval(expr, {"__builtins__":None}, allow_dict)