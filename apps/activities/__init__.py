from django.conf import settings
from activities.models import Activity, Commitment

# Directory in which to save image files for ActivityMember verification.
ACTIVITY_FILE_DIR = getattr(settings, 'ACTIVITY_FILE_DIR', 'activities')

# Maximum number of commitments user can have at one time.
MAX_COMMITMENTS = 5

def get_activities_for_user(user):
  """Gets user's activities, commitments, and goals. Returns a dictionary."""
  
  # TODO: Add goals later since it needs group functionality.
  user_commitments = user.commitment_set.exclude(
    commitmentmember__completed=True,
    commitmentmember__user__username=user.username,
  )
  user_activities = user.activity_set.all()
    
  return {
    "commitments": user_commitments,
    "activities": user_activities,
  }
  
def get_available_activities_for_user(user):
  """Gets the activities, commitments, and goals that the user can participate in."""
  available_commitments = Commitment.get_available_for_user(user)
  available_activities = Activity.get_available_for_user(user)
  
  return {
    "commitments": available_commitments,
    "activities": available_activities,
  }