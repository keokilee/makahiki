import datetime

from django.core import management

from components.activities.models import Activity, ConfirmationCode

class Command(management.base.BaseCommand):
  help = """
  Regenerate the confirmation codes for activities that use confirmation codes. Takes optional parameters to 
  delete the codes for an activity with the specified slug(s)."""
  
  def handle(self, *args, **options):
    """
    Regenerate the confirmation codes for all activities that use confirmation codes.
    """
    # If we don't have any args, find all activities with confirmation type code.
    if len(args) == 0:
      activities = Activity.objects.filter(confirm_type='code')
    else:
      activities = Activity.objects.filter(slug__in=args)
      
    self.stdout.write('The confirmation codes for the following activities will be deleted and regenerated:\n')
    for activity in activities:
      self.stdout.write('%s\n' % activity.title)
      
    self.stdout.write("\nThis process is irreversible.\n")
    value = raw_input("Do you wish to continue (Y/n)? ")
    while value != "Y" and value != "n":
      self.stdout.write("Invalid option %s\n" % value)
      value = raw_input("Do you wish to continue (Y/n)? ")
    if value == "n":
      self.stdout.write("Operation cancelled.\n")
      return
      
    self._regenerate_codes(activities)
      
  def _regenerate_codes(self, activities):
    for activity in activities:
      if not activity.confirm_type == 'code':
        self.stdout.write("ERROR: '%s' has confirmation type %s\n" % (activity.title, activity.confirm_type))
        return
      
      # Generate confirmation codes based on the capacity of this activity
      num_codes = activity.event_max_seat
      
      if not num_codes or num_codes == 0:
        self.stdout.write("ERROR: '%s' has event_max_seat of %d\n" % (activity.title, num_codes))
        return
        
      # Delete confirmation codes for this activity
      self.stdout.write("Deleting old codes for '%s'\n" % activity.title)
      ConfirmationCode.objects.filter(activity=activity).delete()
      
      self.stdout.write("Generating new codes for '%s'\n" % activity.title)
      ConfirmationCode.generate_codes_for_activity(activity, num_codes)
        
    
    
