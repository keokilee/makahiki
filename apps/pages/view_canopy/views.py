from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.views.decorators.cache import never_cache
from django.db.models import Q

from components.canopy.models import Quest, Post

@never_cache
@login_required
def index(request):
  """
  Directs the user to the canopy page.
  """
  canopy_quests = Quest.objects.exclude(users__pk=request.user.pk)
  return render_to_response("canopy/index.html", {
      "canopy_quests": canopy_quests,
  }, context_instance=RequestContext(request))
  
@login_required
def quest_accept(request, slug):
  if request.POST:
    user = request.user
    quest = get_object_or_404(Quest, slug=slug)
    if user not in quest.users.all():
      quest.users.add(user)
    
    return HttpResponseRedirect(reverse("canopy_index"))
    
  raise Http404
  
@login_required
def quest_cancel(request, slug):
  if request.POST:
    user = request.user
    quest = get_object_or_404(Quest, slug=slug)
    if user in quest.users.all():
      quest.users.remove(user)
    
    return HttpResponseRedirect(reverse("canopy_index"))
    
  raise Http404
  