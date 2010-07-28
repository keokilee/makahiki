from django.conf import settings
from activities.models import Activity, Commitment, Goal

# Directory in which to save image files for ActivityMember verification.
ACTIVITY_FILE_DIR = getattr(settings, 'ACTIVITY_FILE_DIR', 'activities')

# Maximum number of commitments user can have at one time.
MAX_COMMITMENTS = 5

# Maximum number of goals a user can participate in at any given time.
MAX_USER_GOALS = 2

# Maximum number of goals a floor can participate in at any given time.
MAX_FLOOR_GOALS = 5

def get_incomplete_tasks(user):
  """Gets user's incomplete activities, commitments, and goals. Returns a dictionary."""
  
  # TODO: Add goals later since it needs group functionality.
  user_commitments = get_current_commitments(user)
  user_activities = get_current_activities(user)
  if user.get_profile().floor:
    user_goals = get_current_goals(user)
    
  else:
    user_goals = None
    
  return {
    "commitments": user_commitments,
    "activities": user_activities,
    "goals": user_goals,
  }
  
def can_add_commitments(user):
  """Determines if the user can add additional commitments."""
  return get_current_commitments(user).count() < MAX_COMMITMENTS
  
def get_current_commitments(user):
  """Get the user's incomplete commitments."""
  return user.commitment_set.filter(
    commitmentmember__award_date=None,
  )
  
def get_available_commitments(user):
  """Get any commitments that the user is not currently active in."""
  return Commitment.objects.exclude(
    commitmentmember__user=user,
    commitmentmember__award_date=None,
  )

def get_completed_commitments(user):
  """Gets the user's completed commitments"""
  return user.commitment_set.exclude(
    commitmentmember__award_date=None
  )
  
def get_current_activities(user):
  """Get the user's incomplete activities."""
  
  return user.activity_set.filter(
    activitymember__award_date=None,
  )
  
def get_available_activities(user):
  """Retrieves only the activities that a user can participate in."""
  
  activities = Activity.objects.exclude(
    activitymember__user=user,
  )
  return (item for item in activities if item.is_active) # Filters out inactive activities.
  
def get_completed_activities(user):
  """Gets the user's completed activities"""
  return user.activity_set.filter(
    activitymember__award_date__isnull=False,
  )
  
def get_current_goals(user):
  """Get the user's incomplete goals. Returns None if the user is not in a floor."""
  
  if user.get_profile().floor:
    return user.get_profile().floor.goal_set.filter(
      goalmember__award_date=None,
    )
    
  return None
  
def get_available_goals(user):
  """Get goals available for the user."""
  if user.get_profile().floor:
    return Goal.objects.exclude(
      goalmember__floor=user.get_profile().floor,
    )
    
  return None

def get_completed_goals(user):
  """Gets the user's completed goals."""
  if user.get_profile().floor:
    return Goal.objects.filter(
      goalmember__floor=user.get_profile().floor,
      goalmember__award_date__isnull=False,
    )
  
  return None
  