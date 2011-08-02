from itertools import chain
from operator import attrgetter

from components.activities import get_current_activity_members, get_current_commitment_members
from components.activities.models import ActivityMember

def get_completed_members(user):
  # Retrieve previously awarded tasks, quests, and badges.
  # Note that we need to check the various activity types because of signup bonuses.
  activity_members = user.activitymember_set.exclude(
    activity__type="activity",
    award_date__isnull=True,
  ).exclude(
    activity__type="survey", 
    approval_status="pending",
  )
    
  commitment_members = user.commitmentmember_set.all()
  quest_members = user.questmember_set.filter(completed=True)
  badge_members = user.badges_earned.all()
    
  for member in badge_members:
    member.updated_at = member.awarded_at
  
  # Merge the querysets, sort according to award_date, and take 5
  # Solution found at:
  # http://stackoverflow.com/questions/431628/how-to-combine-2-or-more-querysets-in-a-django-view
  return sorted(
      chain(activity_members, commitment_members, quest_members, badge_members), 
      key=attrgetter("updated_at"), reverse=True)
      
def get_in_progress_members(user):
  # Retrieve current tasks.
  in_progress_activity_members = get_current_activity_members(user)
  in_progress_commitment_members = get_current_commitment_members(user)
  return sorted(
    chain(in_progress_activity_members, in_progress_commitment_members),
    key=attrgetter("created_at"), reverse=True)