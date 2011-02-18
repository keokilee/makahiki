from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from components.floors.models import Post
from pages.news.forms import WallForm

from pages.news import DEFAULT_POST_COUNT

@login_required
def index(request):
  floor = request.user.get_profile().floor
  
  posts = Post.objects.filter(floor=floor).order_by("-id")
  post_count = posts.count
  posts = posts[:DEFAULT_POST_COUNT]
  more_posts = True if post_count > DEFAULT_POST_COUNT else False
  
  return render_to_response("news/index.html", {
    "posts": posts,
    "wall_form": WallForm(),
    "more_posts": more_posts,
  }, context_instance=RequestContext(request))