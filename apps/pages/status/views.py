# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User

from components.activities import get_popular_tasks
from components.makahiki_base import get_current_round
from components.makahiki_profiles.models import Profile, ScoreboardEntry
from components.prizes.models import RafflePrize


@user_passes_test(lambda u: u.is_staff, login_url="/account/cas/login")
def status(request):
  # Get top point getters in the current round.
  round_name = get_current_round()
  top_users = Profile.objects.order_by("-points", "-last_awarded_submission")[:10]
  if round_name:
    top_profiles = ScoreboardEntry.objects.filter(
        round_name=round_name,
    ).order_by("-points", "-last_awarded_submission")[:10]
    
  # TODO get users who logged in today.
  # TODO get raffle prizes.
  # TODO energy scoreboard
  # TODO most popular activities/commitments
  popular_tasks = get_popular_tasks()
  
  # TODO RSVPs for events.
    
  return render_to_response("status/home.html", {
      "popular_tasks": popular_tasks,
  }, context_instance=RequestContext(request))