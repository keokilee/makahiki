from django.contrib import admin
from django import forms

from goals.models import EnergyGoal

class EnergyGoalAdminForm(forms.ModelForm):
  class Meta:
    model = EnergyGoal
    
  def clean(self):
    """
    Custom clean method that verifies two things:
    
    * The voting end date is after the start of the goal and before the end of the goal.
    * The minimum goal is less than the maximum goal.
    * No existing goals are happening during this time.
    """
    cleaned_data = self.cleaned_data
    
    # Verify dates.
    start_date = cleaned_data["start_date"]
    voting_end_date = cleaned_data["voting_end_date"]
    end_date = cleaned_data["end_date"]
    
    if start_date > voting_end_date:
      message = "The voting end date must be on the same day or after the start date."
      self._errors["voting_end_date"] = self.error_class([message])
      del cleaned_data["voting_end_date"]
    elif end_date <= voting_end_date:
      message = "The end date must be after the voting end date."
      self._errors["end_date"] = self.error_class([message])
      del cleaned_data["end_date"]
      
    # Verify goal values.
    minimum_goal = cleaned_data["minimum_goal"]
    maximum_goal = cleaned_data["maximum_goal"]
    if minimum_goal >= maximum_goal:
      message = "The minimum percent reduction must be less than the maximum."
      self._errors["minimum_goal"] = self.error_class([message])
      del cleaned_data["minimum_goal"]
      
    # Verify that no goals are going on during this time.
    for goal in EnergyGoal.objects.all():
      message = "An energy goal is already running from %s to %s." % (goal.start_date, goal.end_date)
      if start_date > goal.start_date and start_date < goal.end_date:
        self.errors["start_date"] = self.error_class([message])
        del cleaned_data["start_date"]
      elif end_date > goal.start_date and end_date < goal.end_date:
        self.errors["end_date"] = self.error_class([message])
        del cleaned_data["end_date"]
      
    return cleaned_data
      
class EnergyGoalAdmin(admin.ModelAdmin):
  form = EnergyGoalAdminForm
  
  list_display = ["start_date", "voting_end_date", "end_date",]
  
admin.site.register(EnergyGoal, EnergyGoalAdmin)