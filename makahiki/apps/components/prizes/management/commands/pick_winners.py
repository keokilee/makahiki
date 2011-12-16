import random
import datetime

from django.core import management

from components.prizes.models import RaffleDeadline
from components.makahiki_notifications.models import NoticeTemplate, UserNotification

class Command(management.base.BaseCommand):
  help = 'Picks winners for raffle deadlines that have passed.'
  
  def handle(self, *args, **options):
    """
    Picks winners for raffle deadlines that have passed.
    """
    deadlines = RaffleDeadline.objects.filter(end_date__lte=datetime.datetime.today())
    for deadline in deadlines:
      self.stdout.write("Picking winners for %s prizes\n" % deadline.round_name)
      self.__pick_winners(deadline.raffleprize_set.filter(winner__isnull=True))
      
  def __pick_winners(self, prizes):
    for prize in prizes:
      if not prize.winner:
        # Randomly order the tickets and then pick a random ticket.
        while True:
          tickets = prize.raffleticket_set.order_by("?").all()
          if tickets.count() == 0:
            self.stdout.write('No tickets for %s. Skipping.\n' % prize)
          ticket = random.randint(0, tickets.count() - 1)
          user = tickets[ticket].user
          self.stdout.write(str(prize) + ": " + user.username + '\n')
          value = raw_input('Is this OK? [y/n] ')
          if value.lower() == 'y':
            prize.winner = user
            prize.save()
            
            self.stdout.write("Notifying %s\n" % user.username)
            # Notify winner using the template.
            try:
              template = NoticeTemplate.objects.get(notice_type='raffle-winner')
              message = template.render({'PRIZE': prize})
              UserNotification.create_info_notification(user, message, True, prize)
            except NoticeTemplate.DoesNotExist:
              self.stdout.write("Could not find the raffle-winner template.  User was not notified.\n")
              
            break