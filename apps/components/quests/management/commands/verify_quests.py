import sys

from django.core import management
from django.contrib.auth.models import User

from components.quests.models import Quest
from components.quests import process_conditions_string

class Command(management.base.BaseCommand):
  help = "Verifies that all existing quest unlock/completion conditions are valid."
  
  def handle(self, *args, **options):
    print "Validating quests ..."
    for quest in Quest.objects.all():
      error_msg = self.validate_conditions(quest.unlock_conditions)
      if error_msg:
        print "Unlock conditions for '%s' did not validate: %s" % (quest.name, error_msg)

      error_msg = self.validate_conditions(quest.completion_conditions)
      if error_msg:
        print "Completion conditions for '%s' did not validate: %s" % (quest.name, error_msg)
        
  def validate_conditions(self, conditions):
    """
    Validate the conditions string.
    """
    # Pick a user and see if the conditions result is true or false.
    error_msg = None
    user = User.objects.order_by("?")[0]
    try:
      result = process_conditions_string(conditions, user)
      # Check if the result type is a boolean
      if type(result) != type(True):
        error_msg = "Expected boolean value but got %s" % type(result)
    except Exception:
      error_msg = "Received exception: %s" % sys.exc_info()[0]

    return error_msg
    