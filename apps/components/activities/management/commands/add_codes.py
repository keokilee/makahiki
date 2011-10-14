import datetime

from django.core import management

from components.activities.models import Activity, ConfirmationCode

class Command(management.base.BaseCommand):
  help = """
  Add ConfirmationCodes to activities with the specified slug(s)."""
  
  def handle(self, *args, **options):
    """
    Add confirmation codes for the specified activities.
    """
    # If we don't have any args, find all activities with confirmation type code.
    if len(args) < 2:
      self.stdout.write('Usage: python manage.py add_codes <num_codes> <slug1, slug2, ...>\n')
      return
    
    num_codes = 0
    try:
      num_codes = int(args[0])
    except ValueError:
      self.stdout.write('%s is not a valid integer\n' % args[0])
      
    activities = Activity.objects.filter(slug__in=args[1:])
    for activity in activities:
      self.stdout.write("Generating %d additional codes for '%s'.\n" % (num_codes, activity.title))
      ConfirmationCode.generate_codes_for_activity(activity, num_codes)
      
    
        
    
    
