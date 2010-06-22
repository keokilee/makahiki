from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib import messages


from floors.models import Dorm, Floor, Post
from floors.forms import WallForm
from makahiki_avatar.models import Avatar
# Create your views here.

def dorm(request, dorm_slug):
  dorm = get_object_or_404(Dorm, slug=dorm_slug)
  
def floor(request, dorm_slug, floor_slug):
  dorm = get_object_or_404(Dorm, slug=dorm_slug)
  floor = get_object_or_404(Floor, dorm=dorm, slug=floor_slug)
  
  profiles = floor.profile_set.all()[0:12]
  posts = floor.post_set.order_by('-created_at')
  wall_form = WallForm(initial={"floor" : floor.pk})
  
  return render_to_response('floors/floor_detail.html', {
    "profiles": profiles,
    "floor": floor,
    "posts": posts,
    "wall_form": wall_form,
  }, context_instance = RequestContext(request))
  
def floor_members(request, dorm_slug, floor_slug):
  """Lists all of the members of the floor."""
  dorm = get_object_or_404(Dorm, slug=dorm_slug)
  floor = get_object_or_404(Floor, dorm=dorm, slug=floor_slug)
  
  profiles = floor.profile_set.all()
  
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