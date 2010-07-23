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

def get_tasks_for_user(user):
  """Gets user's incomplete activities, commitments, and goals. Returns a dictionary."""
  
  # TODO: Add goals later since it needs group functionality.
  user_commitments = user.commitment_set.filter(
    commitmentmember__award_date=None,
  )
  user_activities = user.activity_set.filter(
    activitymember__award_date=None,
  )
  if user.get_profile().floor:
    user_goals = user.get_profile().floor.goal_set.filter(
      goalmember__floor=user.get_profile().floor,
      goalmember__award_date=None,
    )
    
  else:
    user_goals = None
    
  return {
    "commitments": user_commitments,
    "activities": user_activities,
    "goals": user_goals,
  }
  