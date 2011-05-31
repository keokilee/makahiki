from itertools import chain
from operator import attrgetter

from django.db.models import Q
from django.core.urlresolvers import reverse
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.views.decorators.cache import never_cache

from components.makahiki_base import restricted
from pages.view_profile.forms import ProfileForm
from components.makahiki_facebook.models import FacebookProfile
from components.activities import get_current_activity_members, get_current_commitment_members
from components.activities.models import ActivityMember, CommitmentMember

import components.makahiki_facebook.facebook as facebook

@never_cache
@login_required
def index(request):
  user = request.user
  form = None
  if request.method == "POST":
    user = request.user
    form = ProfileForm(request.POST)
    if form.is_valid():
      profile = user.get_profile()
      profile.name = form.cleaned_data["display_name"]
      profile.about = form.cleaned_data["about"]
      profile.contact_email = form.cleaned_data["contact_email"]
      profile.contact_text = form.cleaned_data["contact_text"]
      profile.contact_carrier = form.cleaned_data["contact_carrier"]
      # profile.enable_help = form.cleaned_data["enable_help"]
      try:
        fb_profile = user.facebookprofile
        fb_profile.can_post = form.cleaned_data["facebook_can_post"]
        fb_profile.save()
      except FacebookProfile.DoesNotExist:
        pass
        
      profile.save()
      form.message = "Your changes have been saved"
    else:
      form.message = "Please correct the errors below."
      
  # If this is a new request, initialize the form.
  if not form:
    try:
      fb_profile = user.facebookprofile
      fb_can_post = fb_profile.can_post
    except FacebookProfile.DoesNotExist:
      fb_can_post = False
      
    form = ProfileForm(initial={
      "enable_help": user.get_profile().enable_help,
      "display_name": user.get_profile().name,
      "about": user.get_profile().about,
      "contact_email": user.get_profile().contact_email or user.email,
      "contact_text": user.get_profile().contact_text,
      "contact_carrier": user.get_profile().contact_carrier,
      "facebook_can_post": fb_can_post,
    })
    
    if request.GET.has_key("changed_avatar"):
      form.message = "Your avatar has been updated."
  
  # Retrieve previously awarded tasks, quests, and badges.
  # Note that we need to check the various activity types because of signup bonuses.
  activity_members = user.activitymember_set.exclude(
    activity__type="activity",
    award_date__isnull=True,
  ).exclude(
    activity__type="survey", 
    approval_status="pending",
  )
    
  commitment_members = user.commitmentmember_set.all()
  quest_members = user.questmember_set.filter(completed=True)
  badge_members = user.badges_earned.all()
    
  for member in badge_members:
    member.updated_at = member.awarded_at
  
  # Merge the querysets, sort according to award_date, and take 5
  # Solution found at http://stackoverflow.com/questions/431628/how-to-combine-2-or-more-querysets-in-a-django-view
  completed_members = sorted(
      chain(activity_members, commitment_members, quest_members, badge_members), 
      key=attrgetter("updated_at"), reverse=True)
  
  # Retrieve current tasks.
  in_progress_activity_members = get_current_activity_members(user)
  in_progress_commitment_members = get_current_commitment_members(user)
  in_progress_members = sorted(
    chain(in_progress_activity_members, in_progress_commitment_members),
    key=attrgetter("created_at"), reverse=True)
  
  # Retrieve Facebook information.
  fb_profile = None
  fb_enabled = False
  try:
    fb_user = facebook.get_user_from_cookie(request.COOKIES, settings.FACEBOOK_APP_ID, settings.FACEBOOK_SECRET_KEY)
    fb_enabled = True
    if fb_user:
      try:
        fb_profile = request.user.facebookprofile
      except FacebookProfile.DoesNotExist:
        fb_profile = FacebookProfile.create_or_update_from_fb_user(request.user, fb_user)
      
  except AttributeError:
    pass
    
  # Check for a rejected activity member.
  rejected_member = None
  if request.GET.has_key("rejected_id"):
    rejected_member = ActivityMember.objects.get(id=request.GET["rejected_id"])
  
  return render_to_response("view_profile/index.html", {
    "form": form,
    "fb_profile": fb_profile,
    "fb_enabled": fb_enabled,
    "in_progress_members": in_progress_members,
    "completed_members": completed_members,
    "rejected_member": rejected_member,
    "help_info": {
      "prefix": "profile_index",
      "count": range(0, 3),
    }
  }, context_instance=RequestContext(request))
