import datetime

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from components.makahiki_base import get_round_info
from components.prizes.models import Prize

@login_required
def index(request):
  floor = request.user.get_profile().floor
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
      else:
        try:
          prize.current_leader = prize.leader(floor)
        except Exception:
          # TODO: Implement this properly.
          prize.current_leader = floor
      
    prize_dict[key] = prizes
    
  return render_to_response("view_prizes/index.html", {
      "prizes": prize_dict,
      "help_info": {
        "prefix": "prizes_index",
        "count": range(0, 2),
      }
  }, context_instance=RequestContext(request))