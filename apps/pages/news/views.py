from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from components.floors.models import Post
from pages.news.forms import WallForm

@login_required
def index(request):
  floor = request.user.get_profile().floor
  posts = Post.objects.filter(floor=floor)[:10]
  return render_to_response("news/index.html", {
    "posts": posts,
    "wall_form": WallForm(),
  }, context_instance=RequestContext(request))