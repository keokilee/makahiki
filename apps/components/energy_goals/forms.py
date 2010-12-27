from django import forms

from components.energy_goals.models import EnergyGoalVote
      
class EnergyGoalVotingForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    """Override to dynamically generate the choices for percent_reduction."""
    
    super(EnergyGoalVotingForm, self).__init__(*args, **kwargs)
    # Instance points to an instance of the model.
    if self.instance and self.instance.goal:
      goal = self.instance.goal
      choices = []
      for i in range(goal.minimum_goal, goal.maximum_goal+1, goal.goal_increments):
        choices.append((i, "%d%%" % (i,)),)
        
      self.fields["percent_reduction"].widget = forms.Select(choices=choices)
      
  class Meta:
    model = EnergyGoalVote
  