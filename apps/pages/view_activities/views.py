import datetime
import simplejson as json

from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.cache import never_cache

from pages.view_activities.forms import *
from components.activities.models import *
from components.activities import *

def index(request):
  return render_to_response("view_activities/index.html", {}, context_instance=RequestContext(request))
    
@login_required
def view_codes(request, activity_id):
  """View the confirmation codes for a given activity."""
  
  if not request.user or not request.user.is_staff:
    raise Http404
    
  activity = get_object_or_404(Activity, pk=activity_id)
  codes = ConfirmationCode.objects.filter(activity=activity)
  if len(codes) == 0:
    raise Http404
  
  return render_to_response("activities/view_codes.html", {
    "activity": activity,
    "codes": codes,
  }, context_instance = RequestContext(request))

### Private methods.

def __add_commitment(request, commitment_id):
  """Commit the current user to the commitment."""
  
  commitment = get_object_or_404(Commitment, pk=commitment_id)
  user = request.user
  
  if not can_add_commitments(user):
    message = "You can only have %d active commitments." % MAX_COMMITMENTS
    user.message_set.create(message=message)
  elif commitment in get_current_commitments(user):
    user.message_set.create(message="You are already committed to this commitment.")
  else:
    # User can commit to this commitment.
    member = CommitmentMember(user=user, commitment=commitment)
    member.save()
    user.message_set.create(message="You are now committed to \"%s\"" % commitment.title)
  
    # Check for Facebook.
    try:
      import makahiki_facebook.facebook as facebook
      
      fb_user = facebook.get_user_from_cookie(request.COOKIES, settings.FACEBOOK_APP_ID, settings.FACEBOOK_SECRET_KEY)
      if fb_user:
        try:
          graph = facebook.GraphAPI(fb_user["access_token"])
          graph.put_object("me", "feed", message="I am now committed to \"%s\" in the Kukui Cup!" % commitment.title)
        except facebook.GraphAPIError:
          # Incorrect user token.
          pass
          
    except ImportError:
      # Facebook not enabled.
      pass
      
  # Redirect back to the referrer or go to the profile if not available.
  next = request.META.get("HTTP_REFERER", reverse("makahiki_profiles.views.profile", args=(request.user.id,)))
  return HttpResponseRedirect(next)

def __remove_active_commitment(request, commitment_id):
  """Removes a user's active commitment.  Inactive commitments cannot be removed except by admins."""
  
  commitment = get_object_or_404(Commitment, pk=commitment_id)
  user = request.user
  commitment_member = get_object_or_404(CommitmentMember, user=user, commitment=commitment, award_date__isnull=True)
  
  commitment_member.delete()
  user.message_set.create(message="Commitment \"%s\" has been removed." % commitment.title)
    
  # Redirect back to the referrer or go to the profile if not available.
  next = request.META.get("HTTP_REFERER", reverse("makahiki_profiles.views.profile", args=(request.user.id,)))
  return HttpResponseRedirect(next)

def __add_activity(request, activity_id):
  """Commit the current user to the activity."""

  activity = get_object_or_404(Activity, pk=activity_id)
  user = request.user

  # Search for an existing activity for this user
  if activity not in user.activity_set.all():
    activity_member = ActivityMember(user=user, activity=activity)
    activity_member.save()
    user.message_set.create(message="You are now participating in the activity \"" + activity.title + "\"")
  else:
    return Http404

  # Redirect back to the referrer or go to the profile if not available.
  next = request.META.get("HTTP_REFERER", reverse("makahiki_profiles.views.profile", args=(request.user.id,)))
  return HttpResponseRedirect(next)

def __remove_activity(request, activity_id):
  """Remove the current user's activity."""

  activity = get_object_or_404(Activity, pk=activity_id)
  user = request.user
  activity_member = get_object_or_404(ActivityMember, user=user, activity=activity)

  activity_member.delete()
  user.message_set.create(message="Your participation in the activity \"" + activity.title + "\" has been removed")
  
  # Redirect back to the referrer or go to the profile if not available.
  next = request.META.get("HTTP_REFERER", reverse("makahiki_profiles.views.profile", args=(request.user.id,)))
  return HttpResponseRedirect(next)
    
def __request_commitment_points(request, commitment_id):
  """Generates a form to add an optional comment."""
  commitment = get_object_or_404(Commitment, pk=commitment_id)
  user = request.user
  membership = None
  
  try:
    membership = CommitmentMember.objects.get(
        user=user, 
        commitment=commitment, 
        completion_date__lte=datetime.date.today(), 
        award_date=None,
    )
    
  except ObjectDoesNotExist:
    user.message_set.create(message="Either the commitment is not active or it is not completed yet.")
    return HttpResponseRedirect(reverse("makahiki_profiles.views.profile", args=(request.user.id,)))
  
  if request.method == "POST":
    form = CommitmentCommentForm(request.POST)
    if form.is_valid():
      # Currently, nothing in the form needs validation, but just to be safe.
      membership.comment = form.cleaned_data["comment"]
      membership.award_date = datetime.datetime.today()
      
      # Points are awarded in the save method.
      membership.save()
      
      message = "You have been awarded %d points for your participation!" % commitment.point_value
      user.message_set.create(message=message)
      return HttpResponseRedirect(reverse("makahiki_profiles.views.profile", args=(request.user.id,)))
    
  form = CommitmentCommentForm()
  return render_to_response("activities/request_commitment_points.html", {
    "form": form,
    "commitment": commitment,
  }, context_instance = RequestContext(request))
    
def __request_activity_points(request, activity_id):
  """Creates a request for points for an activity."""
  
  activity = get_object_or_404(Activity, pk=activity_id)
  user = request.user
  question = None
  activity_member = None
  
  try:
    # Retrieve an existing activity member object if it exists.
    activity_member = ActivityMember.objects.get(user=user, activity=activity)
    if activity_member.award_date:
      user.message_set.create(message="You have already received the points for this activity.")
      return HttpResponseRedirect(reverse("makahiki_profiles.views.profile", args=(request.user.id,)))
      
  except ObjectDoesNotExist:
    pass # Ignore for now.

  if request.method == "POST":
    if activity.confirm_type == "image":
      form = ActivityImageForm(request.POST, request.FILES)
    elif activity.confirm_type == "free":
      form = ActivityFreeResponseForm(request.POST)
    else:
      form = ActivityTextForm(request.POST)
      
    if form.is_valid():
      if not activity_member:
        activity_member = ActivityMember(user=user, activity=activity)
      
      activity_member.user_comment = form.cleaned_data["comment"]
      # Attach image if it is an image form.
      if form.cleaned_data.has_key("image_response"):
        path = activity_image_file_path(user=user, filename=request.FILES['image_response'].name)
        activity_member.image = path
        new_file = activity_member.image.storage.save(path, request.FILES["image_response"])
        activity_member.approval_status = "pending"
        user.message_set.create(message="Your request has been submitted!")
        
      # Attach text prompt question if one is provided
      elif form.cleaned_data.has_key("question"):
        activity_member.question = TextPromptQuestion.objects.get(pk=form.cleaned_data["question"])
        activity_member.response = form.cleaned_data["response"]
        activity_member.approval_status = "pending"
        user.message_set.create(message="Your request has been submitted!")
        
      elif activity.confirm_type == "code":
        # Approve the activity (confirmation code is validated in forms.ActivityTextForm.clean())
        code = ConfirmationCode.objects.get(code=form.cleaned_data["response"])
        code.is_active = False
        code.save()
        activity_member.approval_status = "approved" # Model save method will award the points.
        points = activity_member.activity.point_value
        message = "You have been awarded %d points for your participation!" % points
        user.message_set.create(message=message)
        
      elif activity.confirm_type == "free":
        activity_member.response = form.cleaned_data["response"]
        activity_member.approval_status = "pending"
        user.message_set.create(message="Your request has been submitted!")

      activity_member.save()
      return HttpResponseRedirect(reverse("makahiki_profiles.views.profile", args=(request.user.id,)))
    
  # Create activity request form.
  elif activity.confirm_type == "image":
    form = ActivityImageForm()
  elif activity.confirm_type == "text":
    question = activity.pick_question()
    form = ActivityTextForm(initial={"question" : question.pk})
  elif activity.confirm_type == "free":
    form = ActivityFreeResponseForm()
  else:
    form = ActivityTextForm()
    
  admin_message = activity_member.admin_comment if activity_member else None
      
  return render_to_response("activities/request_activity_points.html", {
    "form": form,
    "activity": activity,
    "question" : question,
    "admin_message": admin_message,
  }, context_instance = RequestContext(request))
  
  
  
  