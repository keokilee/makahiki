import datetime

from django.conf import settings
from activities.models import Activity, Commitment

# Directory in which to save image files for ActivityMember verification.
ACTIVITY_FILE_DIR = getattr(settings, 'ACTIVITY_FILE_DIR', 'activities')

# Maximum number of commitments user can have at one time.
MAX_COMMITMENTS = 5

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
    is_event=False,
    pub_date__lte=datetime.date.today(),
    expire_date__gte=datetime.date.today(),
  ).order_by("priority", "title")
  
  return activities
  
  def get_available_events(user):
    """Retrieves only the events that a user can participate in."""

    events = Activity.objects.exclude(
      activitymember__user=user,
    ).filter(
      is_event=True,
      pub_date__lte=datetime.date.today(),
      expire_date__gte=datetime.date.today(),
    ).order_by("title")

    return events # Filters out inactive activities.

  return (item for item in events if item.is_active) # Filters out inactive activities.
  
def get_completed_activities(user):
  """Gets the user's completed activities"""
  return user.activity_set.filter(
    activitymember__award_date__isnull=False,
  ).order_by("title")
  