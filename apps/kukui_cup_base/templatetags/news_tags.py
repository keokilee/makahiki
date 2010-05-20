import datetime

from django import template

from kukui_cup_base.models import Article

register = template.Library()

def article_date(article):
  format_string = "%m/%d"
  if article.updated_at:
    return article.updated_at.strftime(format_string)
  else:
    return article.created_at.strftime(format_string)
    
register.simple_tag(article_date)