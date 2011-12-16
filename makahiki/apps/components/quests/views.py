import re

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404

from components.quests.models import Quest, QuestMember

@login_required
def accept(request, slug):
  if request.method == "POST":
    referer = request.META["HTTP_REFERER"]
    referer = re.sub(r'\?.*$', '', referer) # Chomp off the query parameters.
    quest = get_object_or_404(Quest, quest_slug=slug)
    if quest.can_add_quest(request.user):
      QuestMember.objects.get_or_create(user=request.user, quest=quest)

    return HttpResponseRedirect(referer)
  
  raise Http404
  
@login_required
def opt_out(request, slug):
  if request.method == "POST":
    referer = request.META["HTTP_REFERER"]
    referer = re.sub(r'\?.*$', '', referer) # Chomp off the query parameters.
    quest = get_object_or_404(Quest, quest_slug=slug)
    if quest.can_add_quest(request.user):
      member, created = QuestMember.objects.get_or_create(user=request.user, quest=quest)
      member.opt_out = True
      member.save()

    return HttpResponseRedirect(referer)
    
  raise Http404
  
@login_required
def cancel(request, slug):
  if request.method == "POST":
    referer = request.META["HTTP_REFERER"]
    referer = re.sub(r'\?.*$', '', referer) # Chomp off the query parameters.
    member = get_object_or_404(QuestMember, quest__quest_slug=slug, user=request.user)
    member.delete()
    return HttpResponseRedirect(referer)
    
  raise Http404