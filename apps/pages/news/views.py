import simplejson as json

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse

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
  
@login_required
def more_posts(request):
  if request.is_ajax():
    floor = request.user.get_profile().floor
    if request.GET.has_key("last_post"):
      posts = Post.objects.filter(floor=floor, id__lt=int(request.GET["last_post"])).order_by("-id")
    else:
      posts = Post.objects.filter(floor=floor).order_by("-id")
    
    post_count = posts.count
    posts = posts[:DEFAULT_POST_COUNT]
    more_posts = True if post_count > DEFAULT_POST_COUNT else False
    
    template = render_to_string("news/news_posts.html", {
        "posts": posts,
        "wall_form": WallForm(),
        "more_posts": more_posts,
    }, context_instance=RequestContext(request))

    return HttpResponse(json.dumps({
        "contents": template,
    }), mimetype='application/json')
  
  raise Http404