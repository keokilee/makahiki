from django.shortcuts import render_to_response
from django.template import RequestContext

from components.floors.models import Post
from pages.news.forms import WallForm

def index(request):
  floor = request.user.get_profile().floor
  posts = Post.objects.filter(floor=floor)[:10]
  return render_to_response("news/index.html", {
    "posts": posts,
    "wall_form": WallForm(),
  }, context_instance=RequestContext(request))