from components.django_cas.backends import CASBackend, _verify
from django.contrib.auth.models import User, AnonymousUser

class MakahikiCASBackend(CASBackend):
  """Checks if the login name is a admin or a participant in the cup."""
  
  def authenticate(self, ticket, service):
      """Verifies CAS ticket and gets or creates User object"""

      username = _verify(ticket, service)
      if not username:
          return None
      try:
          user = User.objects.get(username=username)
      except User.DoesNotExist:
          # TODO: Fix so that non-participants cannot log in.
          user = AnonymousUser()
      return user

