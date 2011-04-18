import datetime

from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.views.decorators.cache import never_cache

from components.makahiki_base import get_round_info, get_current_round
from components.prizes import POINTS_PER_TICKET
from components.prizes.models import Prize, RafflePrize, RaffleDeadline

@login_required
@never_cache
def index(request):
  floor = request.user.get_profile().floor
  prizes = _get_prizes(floor)
  raffle_dict = _get_raffle_prizes(request.user)
    
  return render_to_response("view_prizes/index.html", {
      "prizes": prizes,
      "raffle": raffle_dict,
  }, context_instance=RequestContext(request))
  
@login_required
def add_ticket(request, prize_id):
  """
  Adds a user's raffle ticket to the prize.
  """
  prize = get_object_or_404(RafflePrize, id=prize_id)
  profile = request.user.get_profile()
  if profile.available_tickets > 0:
    prize.add_ticket(request.user)
    return HttpResponseRedirect(reverse("prizes_index"))
    
  raise Http404
  
@login_required
def remove_ticket(request, prize_id):
  """
  Removes a user's raffle ticket from the prize.
  """
  prize = get_object_or_404(RafflePrize, id=prize_id)
  if prize.allocated_tickets(request.user) > 0:
    prize.remove_ticket(request.user)
    return HttpResponseRedirect(reverse("prizes_index"))
    
  raise Http404
  
def _get_prizes(floor):
  """
  Private method to process the prizes half of the page.
  Takes the user's floor and returns a dictionary to be used in the template.
  """
  prizes = Prize.objects.all()
  rounds = get_round_info()
  prize_dict = {}
  today = datetime.datetime.today()
  for key in rounds.keys():
    prizes = Prize.objects.filter(round_name=key)
    for prize in prizes:
      if today < datetime.datetime.strptime(rounds[key]["start"], "%Y-%m-%d"):
        # If the round happens in the future, we don't care who the leader is.
        prize.current_leader = "TBD"
        
      elif prize.competition_type  == "points":
        # If we are in the middle of the round, display the current leader.
        if today < datetime.datetime.strptime(rounds[key]["end"], "%Y-%m-%d"):
          prize.current_leader = prize.leader(floor)
        else:
          prize.winner = prize.leader(floor)
          
      # Else, this is an energy competition prize.
      else:
        # Slugify the round name to create a CSS id.
        prize_id = slugify(key) + "-leader"
        if today < datetime.datetime.strptime(rounds[key]["end"], "%Y-%m-%d"):
          prize.current_leader = "<span id='%s'></span>" % prize_id 
        else:
          prize.winner = "<span id='%s'></span>" % prize_id
      
    prize_dict[key] = prizes
    
  return prize_dict
  
def _get_raffle_prizes(user):
  """
  Private method to process the raffle half of the prize page.
  Takes a user and returns a dictionary to be used in the template.
  """
  current_round = get_current_round()
  today = datetime.datetime.today()
  
  # Get deadline.
  try:
    deadline = RaffleDeadline.objects.get(round_name=current_round)
  except RaffleDeadline.DoesNotExist:
    # TODO; Handle if there is no raffle for this round.
    return None
    
  if today < deadline.pub_date:
    # TODO: Find the pub date of the next round and maybe post something about that.
    deadline = None
    
  # Get the user's tickets.
  profile = user.get_profile()
  available_tickets = profile.available_tickets()
  total_tickets = profile.points / POINTS_PER_TICKET
  allocated_tickets = total_tickets - available_tickets
  
  # Get the prizes for the raffle.
  prizes = RafflePrize.objects.filter(deadline=deadline)
    
  return {
    "deadline": deadline,
    "points_per_ticket": POINTS_PER_TICKET,
    "tickets": {
        "available": available_tickets,
        "total": total_tickets,
        "allocated": allocated_tickets,
    },
    "prizes": prizes,
  }