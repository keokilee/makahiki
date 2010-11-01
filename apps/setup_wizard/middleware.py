from django.contrib import messages

class CheckSetupMiddleware(object):
  def process_request(self, request):
    user = request.user
    if user.is_authenticated() and not user.get_profile().setup_complete:
      # user.message_set.create(message="%s did not complete the setup." % user.username)
      pass
    return None