import simplejson as json

from django.shortcuts import get_object_or_404, render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.views.decorators.cache import never_cache

from makahiki_base import restricted
from floors import NUM_POSTS_TO_DISPLAY
from floors.models import Dorm, Floor, Post
from floors.forms import WallForm
from makahiki_avatar.models import Avatar
from goals.models import EnergyGoal, FloorEnergyGoal
# Create your views here.

@never_cache
def floor(request, dorm_slug, floor_slug):
  dorm = get_object_or_404(Dorm, slug=dorm_slug)
  floor = get_object_or_404(Floor, dorm=dorm, slug=floor_slug)
  
  if not request.user.is_authenticated() or (request.user.get_profile() not in floor.profile_set.all() and not request.user.is_staff):
    return restricted(request, "You must be a member of the floor to access this page.")
    
  profiles = floor.profile_set.all()[0:12]
  posts = floor.post_set.order_by('-created_at')[0:NUM_POSTS_TO_DISPLAY]
  wall_form = WallForm(initial={"floor" : floor.pk})
  
  # Check if we have a current goal.
  goal = EnergyGoal.get_current_goal()
  try:
    floor_goal = floor.floorenergygoal_set.get(goal=goal)
  except FloorEnergyGoal.DoesNotExist:
    floor_goal = None
  
  return render_to_response('floors/floor_detail.html', {
    "profiles": profiles,
    "floor": floor,
    "posts": posts,
    "num_posts_to_display": NUM_POSTS_TO_DISPLAY,
    "wall_form": wall_form,
    "goal": floor_goal,
  }, context_instance=RequestContext(request))
  
def floor_members(request, dorm_slug, floor_slug):
  """Lists all of the members of the floor."""
  dorm = get_object_or_404(Dorm, slug=dorm_slug)
  floor = get_object_or_404(Floor, dorm=dorm, slug=floor_slug)
  
  profiles = floor.profile_set.all()
  if not request.user.is_authenticated() or (request.user.get_profile() not in profiles and not request.user.is_staff):
    return restricted(request, "You must be a member of the floor to access this page.")

  return render_to_response('floors/members.html', {
    "profiles": profiles,
    "floor": floor,
  }, context_instance = RequestContext(request))
  
def wall_post(request, dorm_slug, floor_slug):
  """Post to a floor wall."""
  dorm = get_object_or_404(Dorm, slug=dorm_slug)
  floor = get_object_or_404(Floor, dorm=dorm, slug=floor_slug)
  
  if request.method == "POST":
    form = WallForm(request.POST)
    if form.is_valid():
      post = Post(user=request.user, floor=floor, text=form.cleaned_data["post"])
      post.save()
      messages.success(request, 'Your post was successful!')
      return HttpResponseRedirect(reverse("floors.views.floor", args=(dorm_slug, floor_slug,)))
  
  elif request.method == "GET" and request.GET.has_key("last_post") and request.is_ajax():
    last_post_id = request.GET.get('last_post')
    posts = floor.post_set.filter(
              id__lt=last_post_id,
            ).order_by('-created_at')[0:NUM_POSTS_TO_DISPLAY]

    response = render_to_string("floors/posts/list.html", {
      "posts": posts,
      "num_posts_to_display": NUM_POSTS_TO_DISPLAY,
    })
    
    return HttpResponse(json.dumps({
        "posts": response,
    }), mimetype='application/json')
    
  raise Http404

    
  