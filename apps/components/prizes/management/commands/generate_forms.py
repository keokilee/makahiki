import os
import datetime

from django.db.models import Q
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify
from django.core import management

from components.floors.models import Floor
from components.makahiki_profiles.models import Profile
from components.prizes.models import RaffleDeadline, RafflePrize, Prize

class Command(management.base.BaseCommand):
  help = 'Picks winners for raffle deadlines that have passed.'
  
  def handle(self, *args, **options):
    """
    Generates forms for winners.
    """
    deadlines = RaffleDeadline.objects.filter(end_date__lte=datetime.datetime.today())
    # Seems to be an easy way to generate round information.
    rounds = (deadline.round_name for deadline in deadlines)
    for round_name in rounds:
      self.__generate_forms(round_name)
      
  def __generate_forms(self, round_name):
    round_dir = 'prizes/%s' % round_name
    if not os.path.exists('prizes'):
      os.mkdir('prizes')
    if not os.path.exists(round_dir):
      os.mkdir(round_dir)
      
    self.__generate_raffle_forms(round_dir, round_name)
    self.__generate_prize_forms(round_dir, round_name)
    
  def __generate_raffle_forms(self, round_dir, round_name):
    # Get raffle prizes.
    prizes = RafflePrize.objects.filter(deadline__round_name=round_name, winner__isnull=False)
    for prize in prizes:
      # Render form
      contents = render_to_string('view_prizes/form.txt', {
          'prize': prize,
          'round': round_name
      })
      
      # Write to file
      filename = 'raffle-%s-%s.txt' % (slugify(prize.title), prize.winner.username)
      f = open('%s/%s' % (round_dir, filename), 'w')
      f.write(contents)
      
  def __generate_prize_forms(self, round_dir, round_name):
    prizes = Prize.objects.filter(
        Q(award_to='individual_floor') | Q(award_to='individual_overall'),
        round_name=round_name,
    )
    # Need to calculate winners for each prize.
    for prize in prizes:
      if prize.award_to == 'individual_floor':
        # Need to calculate floor winners for each floor.
        for floor in Floor.objects.all():
          leader = floor.points_leaders(1, round_name)[0].user
          prize.winner = leader
          contents = render_to_string('view_prizes/form.txt', {
              'prize':  prize,
              'round': round_name
          })
          
          filename = '%s-%s-%s.txt' % (floor.dorm.name, floor.number, leader.username)
          f = open('%s/%s' % (round_dir, filename), 'w')
          f.write(contents)
          
      else:
        leader = Profile.points_leaders(1, round_name)[0].user
        prize.winner = leader
        contents = render_to_string('view_prizes/form.txt', {
            'prize':  prize,
            'round': round_name
        })
        
        filename = 'overall-%s.txt' % leader.username
        f = open('%s/%s' % (round_dir, filename), 'w')
        f.write(contents)
        