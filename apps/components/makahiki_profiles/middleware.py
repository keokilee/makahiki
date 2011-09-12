import datetime

from components.makahiki_badges import user_badges
from lib.brabeion import badges

class LoginTrackingMiddleware(object):
  """
  This middleware tracks how many days in a row the user has come to the site.
  """
  
  def process_request(self, request):
    """Checks if the user is logged in and updates the tracking field."""
    user = request.user
    if user.is_authenticated() and user.badges_earned.filter(slug="dailyvisitor").count() == 0:
      profile = request.user.get_profile()
      last_visit = request.user.get_profile().last_visit_date
      today = datetime.date.today()

      # Look for a previous login.
      if last_visit and (today - last_visit) == datetime.timedelta(days=1):
        profile.last_visit_date = today
        profile.daily_visit_count += 1
        profile.save()
        badges.possibly_award_badge(user_badges.DailyVisitorBadge.slug, user=request.user)

      elif not last_visit or (today - last_visit) > datetime.timedelta(days=1):
        # Reset the daily login count.
        profile.last_visit_date = today
        profile.daily_visit_count = 1
        profile.save()
        
    return None