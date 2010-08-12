from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.views.decorators.cache import never_cache

from floors.models import Dorm, Floor, Post
from floors.forms import WallForm
from makahiki_avatar.models import Avatar
# Create your views here.

def dorm(request, dorm_slug):
  dorm = get_object_or_404(Dorm, slug=dorm_slug)

@never_cache
def floor(request, dorm_slug, floor_slug):
  dorm = get_object_or_404(Dorm, slug=dorm_slug)
  floor = get_object_or_404(Floor, dorm=dorm, slug=floor_slug)
  
  if not request.user.is_authenticated() or (request.user.get_profile() not in floor.profile_set.all() and not request.user.is_staff):
    return _restricted(request)
    
  profiles = floor.profile_set.all()[0:12]
  posts = floor.post_set.order_by('-created_at')
  wall_form = WallForm(initial={"floor" : floor.pk})
  
  return render_to_response('floors/floor_detail.html', {
    "profiles": profiles,
    "floor": floor,
    "posts": posts,
    "wall_form": wall_form,
  }, context_instance=RequestContext(request))
  
def floor_members(request, dorm_slug, floor_slug):
  """Lists all of the members of the floor."""
  dorm = get_object_or_404(Dorm, slug=dorm_slug)
  floor = get_object_or_404(Floor, dorm=dorm, slug=floor_slug)
  
  profiles = floor.profile_set.all()
  if not request.user.is_authenticated() or (request.user.get_profile() not in profiles and not request.user.is_staff):
    return _restricted(request)

  return render_to_response('floors/members.html', {
    "profiles": profiles,
    "floor": floor,
  }, context_instance = RequestContext(request))
  
def wall_post(request, dorm_slug, floor_slug):
  dorm = get_object_or_404(Dorm, slug=dorm_slug)
  floor = get_object_or_404(Floor, dorm=dorm, slug=floor_slug)
  
  if request.method == "POST":
    form = WallForm(request.POST)
    if form.is_valid():
      post = Post(user=request.user, floor=floor, text=form.cleaned_data["post"])
      post.save()
      messages.success(request, 'Your post was successful!')
      return HttpResponseRedirect(reverse("floors.views.floor", args=(dorm_slug, floor_slug,)))
  
  raise Http404
  
def _restricted(request):
  """Helper method to return a error message when a user accesses a page they are not allowed to view."""
  
  return render_to_response("restricted.html", {
    "message": "You must be a member of the floor to access this page."
  }, context_instance = RequestContext(request))