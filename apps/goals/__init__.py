from goals.models import EnergyGoal, EnergyGoalVote
from goals.forms import EnergyGoalVotingForm

def get_info_for_user(user):
  current_goal = EnergyGoal.get_current_goal()
  if current_goal:
    form = None 
    in_voting = current_goal.in_voting_period()
    can_vote = in_voting and current_goal.user_can_vote(user)
    if can_vote:
      form = EnergyGoalVotingForm(instance=EnergyGoalVote(user=user, goal=current_goal))
        
    return {
          "goal": current_goal,
          "in_voting": in_voting,
          "form": form,
    }