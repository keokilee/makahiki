import os.path
import urllib2
import simplejson as json

from components.makahiki_avatar.models import Avatar, avatar_file_path
from components.makahiki_avatar.forms import PrimaryAvatarForm, DeleteAvatarForm, FacebookPictureForm
import components.makahiki_facebook.facebook as facebook
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.urlresolvers import reverse

from django.db.models import get_app
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

try:
    notification = get_app('notification')
except ImproperlyConfigured:
    notification = None

try:
    from friends.models import Friendship
    friends = True
except ImportError:
    friends = False

def _get_next(request):
    """
    The part that's the least straightforward about views in this module is how they 
    determine their redirects after they have finished computation.

    In short, they will try and determine the next place to go in the following order:

    1. If there is a variable named ``next`` in the *POST* parameters, the view will
    redirect to that variable's value.
    2. If there is a variable named ``next`` in the *GET* parameters, the view will
    redirect to that variable's value.
    3. If Django can determine the previous page from the HTTP headers, the view will
    redirect to that previous page.
    """
    next = request.POST.get('next', request.GET.get('next', request.META.get('HTTP_REFERER', None)))
    if not next:
        next = request.path
    return next
    
def get_facebook_photo(request):
  """
  Connect to Facebook to get the user's facebook photo..
  """
  if request.is_ajax():
    fb_user = facebook.get_user_from_cookie(request.COOKIES, settings.FACEBOOK_APP_ID, settings.FACEBOOK_SECRET_KEY)
    fb_id = None
    fb_error = None
    if not fb_user:
      return HttpResponse(json.dumps({
          "error": "We could not access your info.  Please log in again."
      }), mimetype="application/json")
    
    try:
      graph = facebook.GraphAPI(fb_user["access_token"])
      graph_profile = graph.get_object("me")
      fb_id = graph_profile["id"]
    except facebook.GraphAPIError:
      return HttpResponse(json.dumps({
          "contents": "Facebook is not available at the moment, please try later",
      }), mimetype='application/json')
      
    
    # Insert the form into the response.
    form = FacebookPictureForm(initial={
      "facebook_photo": "http://graph.facebook.com/%s/picture?type=large" % fb_id
    })
    
    response = render_to_string("makahiki_avatar/avatar_facebook.html", {
      "fb_error": fb_error,
      "fb_id": fb_id,
      "fb_form": form,
    }, context_instance=RequestContext(request))

    return HttpResponse(json.dumps({
        "contents": response,
    }), mimetype='application/json')

  raise Http404

def upload_fb(request):
  """Uploads the user's picture from Facebook."""
  if request.method == "POST":
    form = FacebookPictureForm(request.POST)
    if form.is_valid():
      # Need to download the image from the url and save it.
      photo_temp = NamedTemporaryFile(delete=True)
      fb_url = form.cleaned_data["facebook_photo"]
      photo_temp.write(urllib2.urlopen(fb_url).read())
      photo_temp.flush()
      
      # Delete old avatars if they exist
      # avatars = Avatar.objects.filter(user=request.user)
      # for avatar in avatars:
      #   avatar.avatar.delete()
      #   avatar.delete()
        
      path = avatar_file_path(user=request.user, 
          filename="fb_photo.jpg")
      avatar = Avatar(
          user = request.user,
          primary = True,
          avatar = path,
      )
      # print "saving facebook photo to " + path
      new_file = avatar.avatar.storage.save(path, File(photo_temp))
      avatar.save()
    
      return HttpResponseRedirect(reverse("profile_index") + "?changed_avatar=True")
  
  raise Http404
  
SIZE_LIMIT = 1024 * 1024 * 2 # 2MB size limit

def __handle_uploaded_file(uploaded_file, user):
  if uploaded_file.size > SIZE_LIMIT:
    raise Exception("File is too large")
  
  # Delete old avatars if they exist
  # avatars = Avatar.objects.filter(user=user)
  # for avatar in avatars:
  #   avatar.avatar.delete()
  #   avatar.delete()
    
  path = avatar_file_path(user=user, 
      filename=uploaded_file.name)
      
  avatar = Avatar(
      user = user,
      primary = True,
      avatar = path,
  )
  new_file = avatar.avatar.storage.save(path, uploaded_file)
  avatar.save()
  
def change(request, extra_context={}, next_override=None):
    file_error = None
    avatars = Avatar.objects.filter(user=request.user).order_by('-primary')
    if avatars.count() > 0:
        avatar = avatars[0]
        kwargs = {'initial': {'choice': avatar.id}}
    else:
        avatar = None
        kwargs = {}
    primary_avatar_form = PrimaryAvatarForm(request.POST or None, user=request.user, **kwargs)
    if request.method == "POST":
        updated = False
        if 'avatar' in request.FILES:
            try:
              __handle_uploaded_file(request.FILES['avatar'], request.user)
              updated = True
              return HttpResponseRedirect(reverse("profile_index") + "?changed_avatar=True")
            except Exception:
              file_error = "Uploaded file is larger than 1 MB."
              
        if 'choice' in request.POST and primary_avatar_form.is_valid():
            avatar = Avatar.objects.get(id=
                primary_avatar_form.cleaned_data['choice'])
            avatar.primary = True
            avatar.save()
            updated = True
            
            return HttpResponseRedirect(reverse("profile_index") + "?changed_avatar=True")
        
    fb_user = facebook.get_user_from_cookie(request.COOKIES, settings.FACEBOOK_APP_ID, settings.FACEBOOK_SECRET_KEY)
    fb_id = None
    
    if fb_user:
      try:
        graph = facebook.GraphAPI(fb_user["access_token"])
        graph_profile = graph.get_object("me")
        fb_id = graph_profile["id"]
      except facebook.GraphAPIError:
        pass
      
    fb_form = FacebookPictureForm(initial={
      "facebook_photo": "http://graph.facebook.com/%s/picture?type=large" % fb_id
    })
    return render_to_response(
        'makahiki_avatar/change.html',
        extra_context,
        context_instance = RequestContext(
            request,
            { 'avatar': avatar, 
              'avatars': avatars,
              'primary_avatar_form': primary_avatar_form,
              'next': next_override or _get_next(request), 
              'fb_id': fb_id,
              'fb_form': fb_form,
              'file_error': file_error,
            }
        )
    )
change = login_required(change)

def delete(request, extra_context={}, next_override=None):
    avatars = Avatar.objects.filter(user=request.user).order_by('-primary')
    if avatars.count() > 0:
        avatar = avatars[0]
    else:
        avatar = None
    delete_avatar_form = DeleteAvatarForm(request.POST or None, user=request.user)
    if request.method == 'POST':
        if delete_avatar_form.is_valid():
            ids = delete_avatar_form.cleaned_data['choices']
            if unicode(avatar.id) in ids and avatars.count() > len(ids):
                for a in avatars:
                    if unicode(a.id) not in ids:
                        a.primary = True
                        a.save()
                        if notification:
                          notification.send([request.user], "avatar_updated", {"user": request.user, "avatar": a})
                          notification.send((x['friend'] for x in Friendship.objects.friends_for_user(request.user)), "avatar_friend_updated", {"user": request.user, "avatar": a})
                        break
            Avatar.objects.filter(id__in=ids).delete()
            # request.user.message_set.create(
            #                 message=_("Successfully deleted the requested avatars."))
            return HttpResponseRedirect(next_override or _get_next(request))
    return render_to_response(
        'avatar/confirm_delete.html',
        extra_context,
        context_instance = RequestContext(
            request,
            { 'avatar': avatar, 
              'avatars': avatars,
              'delete_avatar_form': delete_avatar_form,
              'next': next_override or _get_next(request), }
        )
    )
change = login_required(change)
