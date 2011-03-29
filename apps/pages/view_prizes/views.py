import datetime

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
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
    
  return render_to_response("view_prizes/index.html", {
      "prizes": prize_dict,
      "help_info": {
        "prefix": "prizes_index",
        "count": range(0, 2),
      }
  }, context_instance=RequestContext(request))