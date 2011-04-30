from lib.django_cas.backends import CASBackend, _verify
from django.contrib.auth.models import User, AnonymousUser

class MakahikiCASBackend(CASBackend):
  """Checks if the login name is a admin or a participant in the cup."""
  supports_object_permissions = False
  supports_anonymous_user = False
  supports_inactive_user = True
  
  def authenticate(self, ticket, service):
      """Verifies CAS ticket and gets or creates User object"""

      username = _verify(ticket, service)
      if not username:
          return None
      try:
          user = User.objects.get(username=username)
          return user if user.is_active else None
      except User.DoesNotExist:
          return None
