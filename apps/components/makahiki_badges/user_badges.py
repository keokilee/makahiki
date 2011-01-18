from lib.brabeion import badges
from lib.brabieon.base import Badge, BadgeAwarded
from components.makahiki_profiles.models import Profile

class DailyVisitorBadge(badges.MetaBadge):
  slug = "dailyvisitor"
  levels = ["Awarded",]
  events = ["dailyvisitor",]
  multiple = False
  
  def award(self, **state):
    user = state["user"]
    visits = user.get_profile().daily_visit_count
    if visits >= 3:
      return BadgeAwarded()
      
badges.register(DailyVisitorBadge)
  
  