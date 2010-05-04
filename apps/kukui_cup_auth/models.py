from django_cas.backends import CASBackend

class KukuiCupCASBackend(CASBackend):
  """Checks if the login name is a admin or a participant in the cup."""
  
  def authenticate(self, ticket, service):
    user = super(KukuiCupCASBackend, self).authenticate(ticket, service)
    
    if len(user.email) == 0:
      # Not a valid user.
      user.delete()
      return None
    
    return user
  

