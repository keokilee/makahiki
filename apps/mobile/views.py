from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext

from mobile import get_mobile_standings
from makahiki_profiles.models import Profile
from makahiki_base.models import Article
from activities import get_current_commitments
from goals import get_info_for_user

# Create your views here.

def index(request):
  """Method that redirects the user to their profile if they are logged in."""
  if request.user.is_authenticated() and request.user.get_profile().floor:
    return profile(request)
  else:
    return login(request)
  
def login(request):
  """Provides a login link."""
  
  return render_to_response("mobile/login.html", {}, context_instance=RequestContext(request))
  
def profile(request):
  """The home page for logged in users."""
  if not request.user.is_authenticated():
    return HttpResponseRedirect(reverse("mobile.views.login"))
    
  user = request.user
  profile = Profile.objects.get(user=user)
  
  #TODO: Get scoreboard entry for points.
  
  #TODO: Pull in current energy goal.
  goal_info = get_info_for_user(user)
  floor_goal = None
  if goal_info.has_key("floor_goal"):
    floor_goal = goal_info["floor_goal"]
  
  # Retrieve news articles.
  articles = Article.objects.order_by("-created_at")
  
  #Pull in user standings.
  standings = get_mobile_standings(user)
  
  # Pull in user commitments.
  commitments = get_current_commitments(user)
    
  return render_to_response("mobile/profile.html", {
    "profile": profile,
    "articles": articles,
    "commitments": commitments,
    "standings": standings,
    "goal": floor_goal,
  }, context_instance=RequestContext(request))