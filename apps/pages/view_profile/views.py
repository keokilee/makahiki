from itertools import chain
from operator import attrgetter

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

@login_required
def index(request):
  user = request.user
  form = None
  if request.method == "POST":
    user = request.user
    form = ProfileForm(request.POST)
    if form.is_valid():
      profile = user.get_profile()
      profile.name = form.display_name
      profile.about = form.about
      profile.contact_email = form.contact_email
      profile.contact_text = form.contact_text
      profile.contact_carrier = form.contact_carrier
      try:
        fb_profile = user.facebookprofile
        fb_profile.can_post = form.facebook_can_post
        fb_profile.save()
      except FacebookProfile.DoesNotExist:
        pass
        
      profile.save()
      
  # If this is a new request, initialize the form.
  if not form:
    try:
      fb_profile = user.facebookprofile
      fb_can_post = fb_profile.can_post
    except FacebookProfile.DoesNotExist:
      fb_can_post = False
      
    form = ProfileForm(initial={
      "display_name": user.get_profile().name,
      "about": user.get_profile().about,
      "contact_email": user.get_profile().contact_email or user.email,
      "contact_text": user.get_profile().contact_text,
      "contact_carrier": user.get_profile().contact_carrier,
      "facebook_can_post": fb_can_post,
    })
  
  # Retrieve previously awarded tasks.
  completed_activity_members = user.activitymember_set.filter(award_date__isnull=False)[:5]
  completed_commitment_members = user.commitmentmember_set.filter(award_date__isnull=False)[:5]
  
  # Merge the two querysets, sort according to award_date, and take 5
  # Solution found at http://stackoverflow.com/questions/431628/how-to-combine-2-or-more-querysets-in-a-django-view
  completed_members = sorted(
    chain(completed_activity_members, completed_commitment_members),
    key=attrgetter("award_date"), reverse=True)[:5]
    
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
  
  return render_to_response("view_profile/index.html", {
    "form": form,
    "fb_profile": fb_profile,
    "fb_enabled": fb_enabled,
    "in_progress_members": in_progress_members,
    "completed_members": completed_members,
  }, context_instance=RequestContext(request))

@never_cache
def profile(request, user_id, template_name="makahiki_profiles/profile.html"):    
    other_user = get_object_or_404(User, pk=user_id)
    
    # Check that the user has permission to view this profile.
    if request.user.is_authenticated():
        if request.user == other_user:
          is_me = True
        elif other_user.get_profile().floor == request.user.get_profile().floor or request.user.is_staff: 
          is_me = False
        else:
          return restricted(request, "You are not allowed to view this user's profile page.")
    else:
        return restricted(request, "You are not allowed to view this user's profile page.")
        
    # Create initial return dictionary.
    return_dict = {
        "is_me": is_me,
        "activities_enabled": False,
        "other_user": other_user,
        "floor": other_user.get_profile().floor,
    }
    
    # Load activities for the user.
    try:
      from components.activities import get_incomplete_task_members
      return_dict["activities_enabled"] = True
      
      user_activities = get_incomplete_task_members(other_user)
      return_dict["user_commitments"] = user_activities["commitments"]
      return_dict["user_activities"] = user_activities["activities"]
    
    except ImportError:
      pass
      
    # Load standings for user.
    try:
      from components.standings import generate_standings_for_profile
      
      return_dict["standings"] = generate_standings_for_profile(other_user, is_me)
      
    except ImportError:
      pass
      
    # Retrieve the current energy goal.
    try:
      from components.energy_goals import get_info_for_user
      
      if is_me:
        return_dict["energy_goal"] = get_info_for_user(other_user)
    except ImportError:
      pass
      
    return render_to_response(template_name, return_dict, context_instance=RequestContext(request))

@login_required
def profile_edit(request, form_class=ProfileForm, **kwargs):
    
    template_name = kwargs.get("template_name", "makahiki_profiles/profile_edit.html")
    
    if request.is_ajax():
        template_name = kwargs.get(
            "template_name_facebox",
            "makahiki_profiles/profile_edit_facebox.html"
        )
    
    profile = request.user.get_profile()
    
    if request.method == "POST":
        profile_form = form_class(request.POST, instance=profile)
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = request.user
            profile.save()
            return HttpResponseRedirect(reverse("profile_detail", args=[profile.pk]))
    else:
        profile_form = form_class(instance=profile)
        
    fb_profile = None
    fb_enabled = False
    try:
      import makahiki_facebook.facebook as facebook
      
      fb_enabled = True
      fb_user = facebook.get_user_from_cookie(request.COOKIES, settings.FACEBOOK_APP_ID, settings.FACEBOOK_SECRET_KEY)
      if fb_user:
        try:
          fb_profile = request.user.facebookprofile
        except FacebookProfile.DoesNotExist:
          fb_profile = FacebookProfile.create_or_update_from_fb_user(request.user, fb_user)
        
    except ImportError:
      pass
      
    return render_to_response(template_name, {
        "profile": profile,
        "profile_form": profile_form,
        "fb_profile": fb_profile,
        "fb_enabled": fb_enabled,
    }, context_instance=RequestContext(request))
