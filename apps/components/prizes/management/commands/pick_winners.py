import random
import datetime

from django.core import management

from components.prizes.models import RaffleDeadline

class Command(management.base.BaseCommand):
  help = 'Picks winners for raffle deadlines that have passed.'
  
  def handle(self, *args, **options):
    """
    Picks winners for raffle deadlines that have passed.
    """
    deadlines = RaffleDeadline.objects.filter(end_date__lte=datetime.datetime.today())
    for deadline in deadlines:
      self.stdout.write("Picking winners for %s prizes\n" % deadline.round_name)
      self.__pick_winners(deadline.raffleprize_set.all())
      
  def __pick_winners(self, prizes):
    for prize in prizes:
      # Randomly order the tickets and then pick a random ticket.
      tickets = prize.raffleticket_set.order_by("?").all()
      ticket = random.randint(0, tickets.count() - 1)
      user = tickets[ticket].user
      print str(prize) + ": " + user.username
      prize.winner = user
      prize.save()
      
      # TODO: Do we want to notify winners with an email?
    