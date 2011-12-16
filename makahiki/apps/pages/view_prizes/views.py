import datetime

from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
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
  if request.method == "POST":
    prize = get_object_or_404(RafflePrize, id=prize_id)
    deadline = prize.deadline
    profile = request.user.get_profile()
    in_deadline = (deadline.pub_date <= datetime.datetime.today()) and (deadline.end_date >= datetime.datetime.today())
    print profile.available_tickets()
    if profile.available_tickets() > 0 and in_deadline:
      prize.add_ticket(request.user)
      return HttpResponseRedirect(reverse("prizes_index"))
    elif not in_deadline:
      messages.error(request, "The raffle for this round is over.")
      return HttpResponseRedirect(reverse("prizes_index"))
    else:
      messages.error(request, "Sorry, but you do not have any more tickets.")
      return HttpResponseRedirect(reverse("prizes_index"))
    
  raise Http404
  
@login_required
def remove_ticket(request, prize_id):
  """
  Removes a user's raffle ticket from the prize.
  """
  if request.method == "POST":
    prize = get_object_or_404(RafflePrize, id=prize_id)
    if prize.allocated_tickets(request.user) > 0:
      prize.remove_ticket(request.user)
      return HttpResponseRedirect(reverse("prizes_index"))

    else:
      messages.error(request, "Sorry, but you do not have any tickets for this prize.")
      return HttpResponseRedirect(reverse("prizes_index"))
    
  raise Http404
  
@never_cache
@user_passes_test(lambda u: u.is_staff, login_url="/account/cas/login")
def raffle_form(request, prize_id):
  prize = get_object_or_404(RafflePrize, pk=prize_id)
  return render_to_response('view_prizes/form.txt', {
      'raffle': True,
      'prize': prize,
      'round': prize.deadline.round_name
  }, mimetype='text/plain')
  
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
  current_round = get_current_round() or 'Overall'
  today = datetime.datetime.today()
  
  # Get deadline.
  try:
    deadline = RaffleDeadline.objects.get(round_name=current_round)
  except RaffleDeadline.DoesNotExist:
    # TODO; Handle if there is no raffle for this round.
    return None
    
  # Get the user's tickets.
  profile = user.get_profile()
  available_tickets = profile.available_tickets()
  total_tickets = profile.points / POINTS_PER_TICKET
  allocated_tickets = total_tickets - available_tickets
  
  prizes = None
  if deadline.pub_date < today < deadline.end_date:
    # Get the prizes for the raffle.
    prizes = RafflePrize.objects.filter(deadline=deadline).order_by("-value")
  elif today > deadline.end_date:
    # Determine if there are more prizes.
    prizes = RafflePrize.objects.filter(deadline__pub_date__gt=today)
    
  return {
    "deadline": deadline,
    "today": today,
    "points_per_ticket": POINTS_PER_TICKET,
    "tickets": {
        "available": available_tickets,
        "total": total_tickets,
        "allocated": allocated_tickets,
    },
    "prizes": prizes,
  }