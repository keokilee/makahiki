from django import template

register = template.Library()

def user_tickets(raffle_prize, user):
  return str(raffle_prize.allocated_tickets(user))
  
def user_odds(raffle_prize, user):
  total_tickets = raffle_prize.allocated_tickets()
  if total_tickets == 0:
    return "0%"
    
  user_tickets = raffle_prize.allocated_tickets(user)
  odds = (user_tickets * 100 ) / total_tickets
  return "%d%%" % (odds,)
  
register.filter("user_tickets", user_tickets)
register.filter("user_odds", user_odds)