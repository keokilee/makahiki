from lib.brabeion import badges

from components.quests.models import Quest, QuestMember
from components.activities import is_pau
from components.activities.models import ActivityBase, ActivityMember, CommitmentMember, Category
from components.makahiki_notifications.models import UserNotification
from components.prizes.models import RaffleTicket

# The number of quests a user can have at any one time.
MAX_AVAILABLE_QUESTS = 3

def has_task(user, slug=None, task_type=None, name=None):
  """
  Determines if the user is participating in a task.
  In the case of a activity, this returns True if the user submitted or completed the activity.
  In the case of a commitment, this returns True if the user made or completed the commitment.
  In the case of a event or excursion, this returns True if the user entered their attendance code.
  In the case of a survey, this returns True if the user completed the survey.
  
  If a task_type is specified, then it checks to see if a user has completed a task of that type.
  Only one of name and task_type should be specified.
  """
  if not (name or slug) and not task_type:
    raise Exception("Either slug or task_type must be specified.")
    
  # Only provided for backwards compatibility
  if name:
    task = ActivityBase.objects.get(name=name)
    return is_pau(user, task)
  elif slug:
    try:
      task = ActivityBase.objects.get(slug=slug)
      return is_pau(user, task)
    except ActivityBase.DoesNotExist:
      task = ActivityBase.objects.get(name=slug)
      return is_pau(user, task)
  else:
    task_type = task_type.lower()
    if task_type == "commitment":
      return user.commitmentmember_set.count() > 0
    else:
      return user.activitymember_set.filter(activity__type=task_type).count() > 0
      
def completed_task(user, name=None, slug=None, task_type=None):
  """
  Determines if the user has either completed the named task or completed a task of the given type.
  In general, if a user-task member is approved or has an award date, it is completed.
  Only one of name and task_type should be specified.  Specifying neither will raise an Exception.  
  Specifying both will result in an error.
  """
  if not (name or slug) and not task_type:
    raise Exception("Either name or task_type must be specified.")
    
  if task_type:
    task_type = task_type.lower()
    if task_type == "commitment":
      return user.commitmentmember_set.filter(
          award_date__isnull=False,
      ).count() > 0
    else:
      return user.activitymember_set.filter(
          activity__type=task_type,
          approval_status="approved",
      ).count() > 0
    
  task = None
  if slug:
    task = ActivityBase.objects.get(slug=slug)
  else:
    task = ActivityBase.objects.get(name=name)
  
  if task.type == "commitment":
    return user.commitmentmember_set.filter(
        commitment__id=task.id,
        award_date__isnull=False,
    ).count() > 0
  else:
    return user.activitymember_set.filter(
        activity__id=task.id,
        approval_status="approved",
    ).count() > 0
      
  
      
def has_points(user, points, round_name=None):
  """
  Returns True if the user has at least the requested number of points.
  """
  profile = user.get_profile()
  if round_name:
    entry = ScoreboardEntry.objects.get(profile=profile, round_name=round_name)
    return entry.points >= points
  else:
    return profile.points >= points
  
def allocated_ticket(user):
  """
  Returns True if the user has any allocated tickets.
  """
  return user.raffleticket_set.count() > 0
  
def num_tasks_completed(user, num_tasks, category_name=None, task_type=None):
  """
  Returns True if the user has completed the requested number of tasks.
  """
  # Check if we have a type and/or category.
  if task_type:
    task_type = task_type.lower()
    
  category = None
  if category_name:
    category = Category.objects.get(name=category_name)
    
  user_completed = 0
  if not task_type or task_type != "commitment":
    # Build the query for non-commitment tasks.
    query = ActivityMember.objects.filter(
        user=user,
        award_date__isnull=False,
    )
    
    if task_type:
      query.filter(activity__type=task_type)

    if category:
      query.filter(activity__category=category)
    
    user_completed += query.count()
    
  if not task_type or task_type == "commitment":
    # Build the query for commitment tasks.
    query = CommitmentMember.objects.filter(
        user=user,
        award_date__isnull=False,
    )
    
    if category:
      query.filter(commitment__category=category)
      
    user_completed += query.count()
  
  return user_completed >= num_tasks

def badge_awarded(user, badge_slug):
  # print user.badges_earned.values("slug").all().values()
  for badge in user.badges_earned.all():
    if badge.slug == badge_slug:
      return True
      
  return False
  
CONDITIONS = {
  "has_task": has_task, 
  "completed_task": completed_task,
  "has_points": has_points,
  "allocated_ticket": allocated_ticket, 
  "num_tasks_completed": num_tasks_completed, 
  "badge_awarded": badge_awarded,
}

def process_conditions_string(conditions_string, user):
  """
  Utility method to evaluate conditions.
  """
  conditions = conditions_string
  for name in CONDITIONS.keys():
    conditions = conditions.replace(name + "(", name + "(user,")
      
    
  allow_dict = CONDITIONS.copy()
  allow_dict.update({"True": True, "False": False, "user": user})
  
  return eval(conditions, {"__builtins__":None}, allow_dict)
    
def possibly_completed_quests(user):
  """
  Check if the user may have completed one of their quests.
  Returns an array of the completed quests.
  """
  user_quests = user.quest_set.filter(questmember__completed=False, questmember__opt_out=False)
  completed = []
  for quest in user_quests:
    if quest.completed_quest(user):
      member = QuestMember.objects.get(user=user, quest=quest)
      member.completed = True
      member.save()
      completed.append(quest)
      
      # Create quest notification.
      message = "Congratulations! You completed the '%s' quest." % quest.name
      UserNotification.create_success_notification(user, message, display_alert=True)
      
  return completed
   
def get_quests(user):
  """
  Loads the quests for the user.
  Returns a dictionary of two things:
  * The user's current quests (user_quests)
  * Quests the user can participate in (available_quests)
  """
  return_dict = {}
  
  # Check for completed quests.
  possibly_completed_quests(user)
  
  # Load the user's quests
  quests = get_user_quests(user)
  return_dict.update({"user_quests": quests})
  
  # Check if the user can add more quests
  # Note that the second set of quests are not a queryset object.
  if (quests.count() < MAX_AVAILABLE_QUESTS):
    return_dict.update({"available_quests": get_available_quests(user, MAX_AVAILABLE_QUESTS - len(quests))})
  
  return return_dict
    
def get_user_quests(user):
  """
  Get the quests the user is participating in.
  """
  return user.quest_set.filter(
      questmember__user=user,
      questmember__opt_out=False,
      questmember__completed=False
  )
  
def get_available_quests(user, num_quests):
  """
  Get the quests the user could participate in.
  """
  quests = []
  for quest in Quest.objects.exclude(questmember__user=user).order_by('level'):
    if quest.can_add_quest(user):
      quests.append(quest)
      
      if len(quests) == num_quests:
        return quests
        
  return quests