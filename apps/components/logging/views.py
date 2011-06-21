from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required

@login_required
def log_action(request):
  """
  Simple AJAX view for logging actions.  Note that since the logger intercepts requests and responses, 
  this method just returns a success response.
  """
  if request.is_ajax():
    return HttpResponse()
    
  raise Http404