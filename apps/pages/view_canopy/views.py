import simplejson as json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.cache import never_cache
from django.db.models import Q

from components.canopy.models import Quest, Post
from components.makahiki_profiles.models import Profile
from pages.view_canopy.decorators import can_access_canopy
from pages.view_canopy.forms import WallForm

# Number of posts to load at a time.
DEFAULT_POST_COUNT = 10

@login_required
@never_cache
@can_access_canopy
def index(request):
  """
  Directs the user to the canopy page.
  """
  # Load quests
  canopy_quests = Quest.objects.exclude(users__pk=request.user.pk)
  
  # Load wall
  form = WallForm()
  posts = Post.objects.order_by("-id")
  post_count = posts.count()
  posts = posts[:DEFAULT_POST_COUNT]
  more_posts = True if post_count > DEFAULT_POST_COUNT else False
  
  # Load members
  members = User.objects.filter(Q(is_superuser=True) | Q(is_staff=True) | Q(profile__canopy_member=True))
  
  # Load canopy karma scoreboard.
  karma_scoreboard = Profile.objects.filter(
      canopy_member=True,
  ).order_by("-canopy_karma")[:10]
  
  # Check for the about cookie.
  hide_about = False
  if request.COOKIES.has_key("hide-about"):
    hide_about = True
  
  viz = request.REQUEST.get("viz", None)
  
  return render_to_response("canopy/index.html", {
      "in_canopy": True,
      "canopy_quests": canopy_quests,
      "wall_form": form,
      "posts": posts,
      "more_posts": more_posts,
      "members": members,
      "hide_about": hide_about,
      "viz":viz,
      "karma_scoreboard": karma_scoreboard,
  }, context_instance=RequestContext(request))
  
### User methods -------------------------
@login_required
@can_access_canopy
def members(request):
  """
  Lists all of the members of the canopy.
  """
  canopy_quests = Quest.objects.exclude(users__pk=request.user.pk)
  members = User.objects.filter(Q(is_superuser=True) | Q(is_staff=True) | Q(profile__canopy_member=True))
  
  return render_to_response("canopy/directory/members.html", {
      "in_canopy": True,
      "canopy_quests": canopy_quests,
      "members": members,
  }, context_instance=RequestContext(request))
  
### Quest methods -------------------------
@login_required
@can_access_canopy
def quest_accept(request, slug):
  if request.method == "POST":
    user = request.user
    quest = get_object_or_404(Quest, slug=slug)
    if user not in quest.users.all():
      quest.users.add(user)
    
    return HttpResponseRedirect(reverse("canopy_index"))
    
  raise Http404
  
@login_required
@can_access_canopy
def quest_cancel(request, slug):
  if request.method == "POST":
    user = request.user
    quest = get_object_or_404(Quest, slug=slug)
    if user in quest.users.all():
      quest.users.remove(user)
    
    return HttpResponseRedirect(reverse("canopy_index"))
    
  raise Http404
  
@login_required
@can_access_canopy
def post(request):
  if request.method == "POST":
    form = WallForm(request.POST)
    if form.is_valid(): # Should always be valid. Check for content is done on client side.
      post = Post(
          user=request.user,
          text=form.cleaned_data["post"],
      )
      post.save()
    
      if request.is_ajax():
        # Render the post and send it as a response.
        template = render_to_string("canopy/post.html", {"post": post}, 
            context_instance=RequestContext(request))
        return HttpResponse(json.dumps({
          "contents": template,
        }), mimetype="application/json")
      else:
        return HttpResponseRedirect(reverse("canopy_index"))
  
  raise Http404
  
### Wall methods -------------------------
@login_required
@can_access_canopy
def more_posts(request):
  if request.is_ajax():
    floor = request.user.get_profile().floor
    if request.GET.has_key("last_post"):
      posts = Post.objects.filter(id__lt=int(request.GET["last_post"])).order_by("-id")
    else:
      posts = Post.objects.order_by("-id")

    post_count = posts.count()
    posts = posts[:DEFAULT_POST_COUNT]
    more_posts = True if post_count > DEFAULT_POST_COUNT else False

    template = render_to_string("canopy/wall_posts.html", {
        "posts": posts,
        "more_posts": more_posts,
    }, context_instance=RequestContext(request))

    return HttpResponse(json.dumps({
        "contents": template,
    }), mimetype='application/json')

  raise Http404
  