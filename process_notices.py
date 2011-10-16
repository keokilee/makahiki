#!/usr/bin/env python
import sys
import datetime

from os.path import abspath, dirname, join

try:
    import pinax
except ImportError:
    sys.stderr.write("Error: Can't import Pinax. Make sure you have it installed or use pinax-boot.py to properly create a virtual environment.")
    sys.exit(1)

from django.conf import settings
from django.core.management import setup_environ

try:
    import settings as settings_mod # Assumed to be in the same directory.
except ImportError:
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

import sys

# setup the environment before we start accessing things in the settings.
setup_environ(settings_mod)

sys.path.insert(0, join(settings.PINAX_ROOT, "apps"))
sys.path.insert(0, join(settings.PROJECT_ROOT, "apps"))

from components.makahiki_profiles.models import *
from components.makahiki_profiles import *
from components.activities.models import *
from components.makahiki_notifications.models import UserNotification, NoticeTemplate
from components.makahiki_base import in_competition, get_round_info
from django.db.models import Q

def notify_round_started():
  if not in_competition():
    return
    
  today = datetime.datetime.today()
  prev_date = None
  current_round = "Overall Round"
  previous_round = None
  
  for key, value in settings.COMPETITION_ROUNDS.items():
    # We're looking for a round that ends today and another that starts today (or overall)
    start = datetime.datetime.strptime(value["start"], "%Y-%m-%d")
    end = datetime.datetime.strptime(value["end"], "%Y-%m-%d")
    # Check if a round ended in the last 24 hours and check for the current round.
    if abs(today - end) < datetime.timedelta(hours=23):
      previous_round = key
        
    elif start < today < end:
      current_round = key
    
  print previous_round
  print current_round
    
  if current_round and previous_round and current_round != previous_round:
    template = NoticeTemplate.objects.get(notice_type="round-transition")
    message = template.render({"PREVIOUS_ROUND": previous_round, "CURRENT_ROUND": current_round,})
    for user in User.objects.all():
      UserNotification.create_info_notification(user, message, display_alert=True,)
    
def notify_commitment_end():
  members = CommitmentMember.objects.filter(completion_date=datetime.date.today(), award_date__isnull=True)
  
  # try and load the notification template.
  template = None
  try:
    template = NoticeTemplate.objects.get(notice_type="commitment-ready")
  except NoticeTemplate.DoesNotExist:
    pass
    
  for member in members:
    message = None
    if template:
      message = template.render({"COMMITMENT": member.commitment})
    else:
      message = "Your commitment <a href='%s'>%s</a> has end." % (
          reverse("activity_task", args=(member.commitment.type, member.commitment.slug,)),
          member.commitment.title)

      message += "You can click on the link to claim your points."

    UserNotification.create_info_notification(member.user, message, display_alert=True, content_object=member)
    print "created commitment end notification for %s : %s" % (member.user, member.commitment.slug)

def process_rsvp():
  members = ActivityMember.objects.filter(Q(activity__type="event")|Q(activity__type="excursion"),approval_status="pending")

  # try and load the notification template.
  template_noshow = None
  try:
    template_noshow = NoticeTemplate.objects.get(notice_type="event-noshow-penalty")
  except NoticeTemplate.DoesNotExist:
    pass

  template_reminder = None
  try:
    template_reminder = NoticeTemplate.objects.get(notice_type="event-post-reminder")
  except NoticeTemplate.DoesNotExist:
    pass

  for member in members:
      activity = member.activity
      user = member.user
      profile = user.get_profile()
      
      diff = datetime.date.today() - activity.event_date.date()
      if diff.days == 3:
          message = "%s: %s (No Show)" % (activity.type.capitalize(), activity.title)
          profile.remove_points(4, datetime.datetime.today() - datetime.timedelta(minutes=1), message, member)
          profile.save()
          print "removed 4 points from %s for '%s'" % (profile.name, message)
          
          if template_noshow:
            message = template_noshow.render({"ACTIVITY": activity})
          else:
            message = "4 points had been deducted from you, because you signed up but did not enter the confirmation code 2 days after the %s <a href='%s'>%s</a>, " % (
              activity.type.capitalize(), 
              reverse("activity_task", args=(activity.type, activity.slug,)),
              activity.title)
            message += " If you did attend, please click on the link to claim your points and reverse the deduction."
              
          UserNotification.create_info_notification(user, message, display_alert=True, content_object=member)
          print "created no-show penalty notification for %s for %s" % (profile.name, activity.title)
    
      if diff.days == 2:
          if template_reminder:
            message = template_reminder.render({"ACTIVITY": activity})
          else:
            message  = "Hi %s, <p/> We just wanted to remind you that the %s <a href='http://%s%s'>%s</a> had ended. Please click on the link to claim your points." % (            
              profile.name,
              activity.type.capitalize(), 
              Site.objects.get(id=settings.SITE_ID).domain,
              reverse("activity_task", args=(activity.type, activity.slug,)),
              activity.title)  
            message += "<p/>Because you signed up for the event/excursion, if you do not enter the confirmation code within 2 days after the event/excusion, a total of 4 points (2 point signup bonus plus 2 point no-show penalty) will be deducted from your total points. So please enter your confirmation code early to avoid the penalty."
            message += "<p/><p/>Kukui Cup Administrators"           
          subject = "[Kukui Cup] Reminder to enter your event/excursion confirmation code"
          UserNotification.create_email_notification(user.email, subject, message, message)    
          print "sent post event email reminder to %s for %s" % (profile.name, activity.title)
              
if __name__ == "__main__":
    process_rsvp()
    notify_commitment_end()
    notify_round_started()
