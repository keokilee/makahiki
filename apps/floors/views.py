from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import Http404

from floors.models import Dorm, Floor
from floors.forms import WallForm
from makahiki_avatar.models import Avatar
# Create your views here.

def dorm(request, dorm_slug):
  dorm = get_object_or_404(Dorm, slug=dorm_slug)
  
def floor(request, dorm_slug, floor_slug):
  dorm = get_object_or_404(Dorm, slug=dorm_slug)
  floor = get_object_or_404(Floor, dorm=dorm, slug=floor_slug)
  
  profiles = floor.profile_set.all()
  posts = floor.post_set.order_by('-created_at')
  wall_form = WallForm(initial={"floor" : floor.pk})
  
  return render_to_response('floors/floor_detail.html', {
    "profiles": profiles,
    "floor": floor,
    "posts": posts,
    "wall_form": wall_form,
  }, context_instance = RequestContext(request))
  
def wall_post(request, dorm_slug, floor_slug):
  if request.method == "POST":
    pass
  else:
    raise Http404