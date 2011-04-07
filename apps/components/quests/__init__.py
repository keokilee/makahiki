from lib.brabeion import badges

from components.quests.models import Quest, QuestMember
from components.activities import is_pau
from components.activities.models import ActivityBase, ActivityMember, CommitmentMember

# The number of quests a user can have at any one time.
MAX_AVAILABLE_QUESTS = 3

def has_task(user, task_name):
  """
  Determines if the user is participating in a task.
  In the case of a activity, this returns True if the user submitted or completed the activity.
  In the case of a commitment, this returns True if the user made or completed the commitment.
  In the case of a event or excursion, this returns True if the user entered their attendance code.
  In the case of a survey, this returns True if the user completed the survey.
  """
  task = ActivityBase.objects.get(name=task_name)
  return is_pau(user, task)
  
def allocated_tickets(user):
  """
  Returns True if the user has ever allocated tickets.
  """
  # TODO: Implement when the raffle is implemented.
  raise Exception("Not implemented yet")
  
def num_activities_completed(user, num_activities, category=None):
  """
  Returns True if the user has completed the requested number of tasks.
  """
  if category:
    user_completed = ActivityMember.objects.filter(
        user=user,
        award_date__isnull=False,
    ).count()
    user_completed = user_completed + CommitmentMember.objects.filter(
        user=user,
        award_date__isnull=False
    ).count()
  else:
    user_completed = ActivityMember.objects.filter(
        user=user,
        award_date__isnull=False
    ).count()
    user_completed = user_completed + CommitmentMember.objects.filter(
        user=user,
        award_date__isnull=False
    ).count()
  
  return user_completed >= num_activities

def badge_awarded(user, badge_slug):
  # print user.badges_earned.values("slug").all().values()
  for badge in user.badges_earned.all():
    if badge.slug == badge_slug:
      return True
      
  return False
  
CONDITIONS = {
  "has_task": has_task, 
  "allocated_tickets": allocated_tickets, 
  "num_activities_completed": num_activities_completed, 
  "badge_awarded": badge_awarded,
}

def possibly_complete_quests(user):
  """Check if the user may have completed one of their quests."""
  user_quests = user.quest_set.filter(questmember__completed=False)
  for quest in user_quests:
    if quest.completed_quest(user):
      member = QuestMember.objects.get(user=user, quest=quest)
      member.completed = True
      member.save()
  
def get_quests(user):
  """
  Get the quests for the user.
  """
  # Get the user's incomplete quests.
  incomplete_quests = user.quest_set.filter(
      questmember__user=user,
      questmember__opt_out=False,
      questmember__completed=False
  )
  
  quest_count = incomplete_quests.count()
  if quest_count < MAX_AVAILABLE_QUESTS:
    # If the user doesn't have enough quests, go find some.
    for quest in Quest.objects.exclude(questmember__user=user):
      if quest.can_add_quest(user):
        member = QuestMember(user=user, quest=quest)
        member.save()
        
        quest_count = quest_count + 1
        if quest_count == MAX_AVAILABLE_QUESTS:
          break
  
    return user.quest_set.filter(
        questmember__user=user,
        questmember__opt_out=False,
        questmember__completed=False
    )
  else:
    return incomplete_quests