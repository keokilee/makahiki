from django.core.cache import cache
from django.utils.hashcompat import md5_constructor
from django.utils.http import urlquote

def invalidate_template_cache(fragment_name, *variables):
  """
  Takes the name of the cache as well as additional arguments to invalidate the 
  cache for the template.
  
  Credit to http://djangosnippets.org/snippets/1593/
  """
  args = md5_constructor(u':'.join([urlquote(var) for var in variables]))
  cache_key = 'template.cache.%s.%s' % (fragment_name, args.hexdigest())
  cache.delete(cache_key)
  
def invalidate_info_bar_cache(user):
  """
  Invalidates the user and lounge caches of the info bar.
  """
  invalidate_template_cache("infobar", user.username)
  floor = user.get_profile().floor
  if floor:
    invalidate_template_cache("infobar", floor.dorm.name, floor.number)

def invalidate_floor_avatar_cache(task, user):
  """
  Invalidates task completed avatar list cache.
  """
  if task and user and user.get_profile() and user.get_profile().floor:
    invalidate_template_cache("floor_avatar", task.id, user.get_profile().floor.id)
    
def invalidate_commitments_cache(user):
  """
  Invalidates the cache of the commitments list for the user.
  """
  invalidate_template_cache("commitments", user.username)
  
  