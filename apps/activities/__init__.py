from django.conf import settings
from activities.models import Activity, Commitment

# Directory in which to save image files for ActivityMember verification.
ACTIVITY_FILE_DIR = getattr(settings, 'ACTIVITY_FILE_DIR', 'activities')

# Maximum number of commitments user can have at one time.
MAX_COMMITMENTS = 5

def get_activities_for_user(user):
  """Gets user's activities, commitments, and goals. Returns a dictionary."""
  
  # TODO: Add goals later since it needs group functionality.
  user_commitments = user.commitment_set.filter(
    commitmentmember__completed=False,
  )
  user_activities = user.activity_set.filter(
    activitymember__user=user,
    activitymember__awarded=False,
  )
  user_goals = user.get_profile().floor.goal_set.filter(
    goalmember__floor=user.get_profile().floor,
    goalmember__awarded=False,
  )
    
  return {
    "commitments": user_commitments,
    "activities": user_activities,
    "goals": user_goals,
  }
