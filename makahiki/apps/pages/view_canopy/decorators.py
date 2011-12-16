from functools import wraps
from django.utils.decorators import available_attrs

from django.http import Http404

def can_access_canopy(function=None):
  def decorator(view_func):
    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):
      user = request.user
      if user.is_superuser or user.is_staff or user.get_profile().canopy_member:
        return view_func(request, *args, **kwargs)
      raise Http404
        
    return _wrapped_view
    
  return decorator(function)