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
        tickets = prize.raffleticket_set.order_by("?").all()
        ticket = random.randint(0, tickets.count() - 1)
        user = tickets[ticket].user
        print str(prize) + ": " + user.username
        prize.winner = user
        prize.save()
      
        # Notify winner using the template.
        try:
          template = NoticeTemplate.objects.get(slug='raffle-winner')
          message = template.render({'PRIZE': prize})
          UserNotification.create_info_notification(user, message, True, prize)
        except NoticeTemplate.DoesNotExist:
          self.stdout.write("Could not find the raffle-winner template.  User was not notified.")