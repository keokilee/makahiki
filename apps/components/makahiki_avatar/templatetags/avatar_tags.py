import urllib

from django import template
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.utils.hashcompat import md5_constructor
from django.core.cache import cache

from components.makahiki_avatar import AVATAR_DEFAULT_URL, AVATAR_GRAVATAR_BACKUP

register = template.Library()

def avatar_url(user, size=80):
    if not isinstance(user, User):
        try:
            user = User.objects.get(username=user)
        except User.DoesNotExist:
            return AVATAR_DEFAULT_URL
            
    # Try and get the avatar from cache first.
    avatar = cache.get('avatar-%s' % user.username)
    if not avatar:
        avatars = user.avatar_set.order_by('-date_uploaded')
        primary = avatars.filter(primary=True)
        if primary.count() > 0:
            avatar = primary[0]
        elif avatars.count() > 0:
            avatar = avatars[0]
        
        # Update cache.
        if avatar is not None:
            cache.set('avatar-%s' % user.username, avatar, 60 * 60 *24)
        
    if avatar is not None:
        if not avatar.thumbnail_exists(size):
            avatar.create_thumbnail(size)
        user_avatar = avatar.avatar_url(size)
    else:
        if AVATAR_GRAVATAR_BACKUP:
            user_avatar = "http://www.gravatar.com/avatar/%s/?%s" % (
                md5_constructor(user.email).hexdigest(),
                urllib.urlencode({'s': str(size)}),)
        else:
            user_avatar = AVATAR_DEFAULT_URL
            
    return user_avatar
    
register.simple_tag(avatar_url)

def avatar(user, size=80):
    if not isinstance(user, User):
        try:
            user = User.objects.get(username=user)
            alt = unicode(user)
            url = avatar_url(user, size)
        except User.DoesNotExist:
            url = AVATAR_DEFAULT_URL
            alt = _("Default Avatar")
    else:
        alt = unicode(user)
        url = avatar_url(user, size)
    return """<img src="%s" alt="%s" width="%s" height="%s" />""" % (url, alt,
        size, size)
register.simple_tag(avatar)

def render_avatar(avatar, size=80):
    if not avatar.thumbnail_exists(size):
        avatar.create_thumbnail(size)
    return """<img src="%s" alt="%s" width="%s" height="%s" />""" % (
        avatar.avatar_url(size), str(avatar), size, size)
register.simple_tag(render_avatar)