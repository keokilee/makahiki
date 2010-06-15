from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from floors.models import Dorm, Floor
from makahiki_avatar.models import Avatar
# Create your views here.

def dorm(request, dorm_slug):
  dorm = get_object_or_404(Dorm, slug=dorm_slug)
  
def floor(request, dorm_slug, floor_slug):
  dorm = get_object_or_404(Dorm, slug=dorm_slug)
  floor = get_object_or_404(Floor, dorm=dorm, slug=floor_slug)
  
  profiles = floor.profile_set.all()
  
  return render_to_response('floors/floor_detail.html', {
    "profiles": profiles,
  }, context_instance = RequestContext(request))