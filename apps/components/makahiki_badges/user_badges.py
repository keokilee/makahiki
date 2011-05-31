from lib.brabeion import badges
from lib.brabeion.base import Badge, BadgeAwarded

class DailyVisitorBadge(Badge):
  name = "Daily Visitor"
  description = [
    "Visited the site 3 days in a row.",
  ]
  hint = "Keep coming back!"
  slug = "dailyvisitor"
  levels = ["Awarded",]
  events = ["dailyvisitor",]
  multiple = False
  image = "images/badges/Threepeater.gif"
  
  def award(self, **state):
    user = state["user"]
    visits = user.get_profile().daily_visit_count
    if visits >= 3:
      return BadgeAwarded()

class FullyCommittedBadge(Badge):
  name = "Fully Committed"
  description = [
    "Participating in 5 commitments at the same time.",
  ]
  hint = "How committed are you?"
  slug = "fully_committed"
  levels = ["Awarded",]
  events = ["fully_committed",]
  multiple = False
  image = "images/badges/badge.gif"
  
  def award(self, **state):
    user = state["user"]
    current_members = user.commitmentmember_set.filter(
        award_date__isnull=True
    )
    if current_members.count() == 5:
      return BadgeAwarded()
      


  