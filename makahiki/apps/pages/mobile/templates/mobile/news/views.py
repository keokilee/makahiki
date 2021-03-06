import simplejson as json

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views.decorators.cache import never_cache
from django.contrib.auth.models import User 
from components.floors.models import Post 
from pages.news.forms import WallForm
from django.core.urlresolvers import reverse
from pages.news import DEFAULT_POST_COUNT

@never_cache
@login_required
def news(request):
  floor = request.user.get_profile().floor
  
  # Get floor posts.
  posts = Post.objects.filter(floor=floor).order_by("-id")
  post_count = posts.count
  posts = posts[:DEFAULT_POST_COUNT]
  more_posts = True if post_count > DEFAULT_POST_COUNT else False
  next=1
  last=0 
  # Get the floor members.
  floor_members = User.objects.filter(profile__floor=request.user.get_profile().floor).order_by("-profile__points")[:12]
  
  return render_to_response("mobile/news/templates/index.html", {
    "next": next,
    "last": last, 
    "posts": posts, 
    "wall_form": WallForm(),
    "more_posts": more_posts, 
    "floor_members": floor_members, 
  }, context_instance=RequestContext(request))

@never_cache
@login_required
def floor_members(request):
  floor_members = User.objects.filter(profile__floor=request.user.get_profile().floor).order_by("-profile__points")
  
  return render_to_response("news/directory/floor_members.html", {
    "floor_members": floor_members,
  }, context_instance=RequestContext(request))
  
@login_required
def post(request):
  if request.is_ajax() and request.method == "POST":
    form = WallForm(request.POST)
    if form.is_valid():
      post = Post(
          user=request.user, 
          floor=request.user.get_profile().floor, 
          text=form.cleaned_data["post"]
      )
      post.save()
      
      # Render the post and send it as a response.
      template = render_to_string("news/user_post.html", {"post": post}, 
          context_instance=RequestContext(request))
      return HttpResponseRedirect(reverse("mobile_news_index"))
      return HttpResponse(json.dumps({
        "contents": template,
      }), mimetype="application/json")
    return HttpResponseRedirect(reverse("mobile_news_index"))

    # At this point there is a form validation error.
    return HttpResponse(json.dumps({
        "message": "This should not be blank."
    }), mimetype="application/json")
  
  raise Http404

@login_required
def more_posts(request,pages): 
  page = int(pages)
  if(page <= 0):
    page=1
  floor = request.user.get_profile().floor
  posts=None
  posts = Post.objects.filter(floor=floor).order_by("-id")
    
  post_count = posts.count
  posts = posts[((page-1)*DEFAULT_POST_COUNT):(page*DEFAULT_POST_COUNT)]
  more_posts = True if post_count > (DEFAULT_POST_COUNT * page) else False
  next=page+1
  last=page-1
  return render_to_response("mobile/news/templates/index.html", {
    "next": next,
    "last": last,
    "posts": posts, 
    "wall_form": WallForm(),
    "more_posts": more_posts, 
    "floor_members": floor_members, 
  }, context_instance=RequestContext(request))
  
  raise Http404
