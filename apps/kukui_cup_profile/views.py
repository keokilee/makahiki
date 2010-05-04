# Create your views here.

from django.core.urlresolvers import reverse
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from kukui_cup_profile.models import Profile
from kukui_cup_profile.forms import ProfileForm


if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None


def profiles(request, template_name="kukui_cup_profile/profiles.html"):
    users = User.objects.all().order_by("-date_joined")
    search_terms = request.GET.get('search', '')
    order = request.GET.get('order')
    if not order:
        order = 'date'
    if search_terms:
        users = users.filter(username__icontains=search_terms)
    if order == 'date':
        users = users.order_by("-date_joined")
    elif order == 'name':
        users = users.order_by("username")
    return render_to_response(template_name, {
        'users':users,
        'order' : order,
        'search_terms' : search_terms
    }, context_instance=RequestContext(request))


def profile(request, username, template_name="kukui_cup_profile/profile.html"):
    
    other_user = get_object_or_404(User, username=username)
    
    if request.user.is_authenticated():
        if request.user == other_user:
            is_me = True
        else:
            is_me = False
    else:
        is_me = False
        
    # Load activities for the user.
    available_commitments = user_commitments = available_activities = user_activities = None
    activities_enabled = False
    try:
      # TODO: Add goals later since it needs group functionality.
      from activities.models import Commitment, Activity
      activities_enabled = True
      
      user_commitments = other_user.commitment_set.all()
      user_activities = other_user.activity_set.all()
      
      if is_me:
        available_commitments = Commitment.objects.exclude(commitmentmember__user__username=request.user.username)
        available_activities = Activity.get_available_for_user(request.user)
    except ImportError:
      pass
    
    return render_to_response(template_name, {
        "is_me": is_me,
        "activities_enabled": activities_enabled,
        "other_user": other_user,
        "available_commitments": available_commitments,
        "user_commitments": user_commitments,
        "available_activities": available_activities,
        "user_activities": user_activities,
    }, context_instance=RequestContext(request))


@login_required
def profile_edit(request, form_class=ProfileForm, **kwargs):
    
    template_name = kwargs.get("template_name", "kukui_cup_profile/profile_edit.html")
    
    if request.is_ajax():
        template_name = kwargs.get(
            "template_name_facebox",
            "kukui_cup_profile/profile_edit_facebox.html"
        )
    
    profile = request.user.get_profile()
    
    if request.method == "POST":
        profile_form = form_class(request.POST, instance=profile)
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = request.user
            profile.save()
            return HttpResponseRedirect(reverse("profile_detail", args=[request.user.username]))
    else:
        profile_form = form_class(instance=profile)
    
    return render_to_response(template_name, {
        "profile": profile,
        "profile_form": profile_form,
    }, context_instance=RequestContext(request))

