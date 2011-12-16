import datetime

from django.core.management.base import BaseCommand

from components.energy_goals.models import EnergyGoal, FloorEnergyGoal
from components.floors.models import Floor

class Command(BaseCommand):
  help = "Process the results of goal voting."
  
  def handle(self, *args, **options):
    goal = EnergyGoal.get_current_goal()
    today = datetime.date.today()
    if goal and goal.voting_end_date <= today and goal.floorenergygoal_set.count() == 0:
      self.stdout.write("Generating goals for each floor.\n")
      # Go through the votes and create energy goals for the floor.
      for floor in Floor.objects.all():
        results = goal.get_floor_results(floor)
        percent_reduction = 0
        if len(results) > 0:
          percent_reduction = results[0]["percent_reduction"]

        floor_goal = FloorEnergyGoal(floor=floor, goal=goal, percent_reduction=percent_reduction)
        floor_goal.save()
        
    elif not goal:
      self.stdout.write("There is no goal to process.\n")
    else:
      self.stdout.write("The floor goals are already created.\n")