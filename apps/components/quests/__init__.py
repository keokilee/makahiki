from components.quests.models import Quest, QuestMember

CONDITIONS = {
  "has_activity": has_activity, 
  "submitted_activity": submitted_activity, 
  "allocated_tickets": allocated_tickets, 
  "num_activities_completed": num_activities_completed, 
  "badge_awarded": badge_awarded,
}

def has_activity(user, activity):
  pass
  
def submitted_activity(user, activity):
  pass
  
def allocated_tickets(user):
  pass
  
def num_activities_completed(user, num_activities):
  pass

def badge_awarded(user, badge):
  pass

def check_quest_completion(user):
  """
  Check if the user has completed any quests.
  """
  pass

def is_complete(user, quest):
  """
  Determine if the user has completed the quest.
  """
  pass
  
def populate_quests(user):
  """
  Load available quests for the user.
  """
  pass
  
def is_available(user, quest):
  """
  Determine if the quest is available for the user.
  """
  pass