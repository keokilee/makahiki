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
  current_round = 'Overall'
  previous_round = None
  
  for key, value in settings.COMPETITION_ROUNDS.items():
    # We're looking for a round that ends today and another that starts today (or overall)
    start = datetime.datetime.strptime(value["start"], "%Y-%m-%d")
    end = datetime.datetime.strptime(value["end"], "%Y-%m-%d")
    # We want a round that ended in the last 24 hours and a round that started in the last 24 hours.
    if end - today < datetime.timedelta(hours=24):
      previous_round = key
    elif start - today < datetime.timedelta(hours=24):
      current_round = key
  
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
    #print "%s : %s" % (member.user, message)

    UserNotification.create_info_notification(member.user, message, display_alert=True, content_object=member)


def process_rsvp():
  members = ActivityMember.objects.filter(Q(activity__type="event")|Q(activity__type="excursion"),approval_status="pending")
  for member in members:
      activity = member.activity
      user = member.user
      profile = user.get_profile()
      
      if member._has_noshow_penalty():
          message = "%s: %s (No Show)" % (activity.type.capitalize(), activity.title)
          profile.remove_points(4, datetime.datetime.today() - datetime.timedelta(minutes=1), message, member)
          profile.save()
          print "remove 4 points from '%s' for '%s'" % (profile.name, message)
      else:
          diff = datetime.date.today() - member.submission_date.date()
          if diff.days > 1:
              #create a email reminder
              EmailReminder.objects.create(
                  user=user,
                  activity=activity,
                  email_address=profile.contact_email,
                  send_at=member.submission_date + datetime.timedelta(days=1)
                  )
              
              print "create email reminder for %s" % profile.contact_email
              
if __name__ == "__main__":
    #process_rsvp()
    notify_commitment_end()
    notify_round_started()
