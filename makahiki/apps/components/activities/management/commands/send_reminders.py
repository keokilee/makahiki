import datetime

from django.core import management

from components.activities.models import EmailReminder, TextReminder

class Command(management.base.BaseCommand):
  help = 'Sends out pending reminders if their send_at time has passed.'
  
  def handle(self, *args, **options):
    """
    Sends out pending reminders if their send_at time has passed.
    """
    self.stdout.write('****** Checking reminders for %s *******\n' % datetime.datetime.today())
    reminders = EmailReminder.objects.filter(
        send_at__lte=datetime.datetime.today(),
        sent=False,
    )
    for reminder in reminders:
      self.stdout.write("\nSending reminder to %s for '%s'\n" % (reminder.email_address, reminder.activity.title))
      reminder.send()
      
    reminders = TextReminder.objects.filter(
        send_at__lte=datetime.datetime.today(),
        sent=False,
    )
    for reminder in reminders:
      self.stdout.write("\nSending reminder to %s for '%s'\n" % (reminder.text_number, reminder.activity.title))
      reminder.send()
    
      