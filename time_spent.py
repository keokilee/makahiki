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

from django.contrib.auth.models import User
from django.db.models import Q

from components.analytics.models import MakahikiLog

def calculate_user_time():
    users_file = open('time_spent_users.csv', 'w')
    lounge_file = open('time_spent_lounge.csv', 'w')
    users = User.objects.filter(profile__points__gt=0, is_staff=False)
    lounges = {}
    counter = 1
    user_count = users.count()
    for user in users:
        logs = MakahikiLog.objects.filter(remote_user=user.username).order_by('request_time')
        sys.stdout.write('Processing %d logs for %s (%d/%d)\n' % (logs.count(), user.username, counter, user_count))
        total = _time_spent(logs)
        activity_time = _page_time('/activities', logs)
        energy_time = _page_time('/energy', logs)
        prize_time = _page_time('/prizes', logs)
        
        users_file.write('%s,%d,%d,%d,%d\n' % (user.username, total, activity_time, energy_time, prize_time))
        lounge = str(user.get_profile().floor)
        lounges[lounge] = lounges.get(lounge, {})
        lounges[lounge]['total'] = lounges[lounge].get('total', 0) + total
        lounges[lounge]['activities'] = lounges[lounge].get('activities', 0) + activity_time
        lounges[lounge]['energy'] = lounges[lounge].get('energy', 0) + energy_time
        lounges[lounge]['prizes'] = lounges[lounge].get('prizes', 0) + prize_time
        counter += 1
        
    for lounge, items in lounges.iteritems():
        lounge_file.write('%s,%d,%d,%d,%d\n' % (lounge, items['total'], items['activities'], items['energy'], items['prizes']))
        
    lounge_file.close()
    users_file.close()
    
def _time_spent(logs):
    # Iterate over the logs and track previous time and time spent.
    prev = datetime.datetime.strptime(logs[0].request_time, "%Y-%m-%d %H:%M:%S")
    cur_session = total = 0
    
    for log in logs[1:]:
        current = datetime.datetime.strptime(log.request_time, "%Y-%m-%d %H:%M:%S")
        diff = current - prev
        # Start a new interval if 30 minutes have passed.
        if diff.total_seconds() > (60 * 30):
            if cur_session == 0:
                total += 60 # Assume they spent a minute viewing a single page.
            else:
                total += cur_session
            cur_session = 0
        else:
            cur_session += diff.total_seconds()
            
        prev = current
        
    # Append any session that was in progress.
    total += cur_session
    return total
    
def _page_time(url_prefix, logs):
    start = prev = None
    total = cur_session = 0
    # Need to filter out AJAX interactions.
    for log in logs.exclude(Q(url__startswith='/log') | Q(url__startswith='/slog') | Q(url__startswith='/notifications') | Q(url__startswith='/quests')):
        current = datetime.datetime.strptime(log.request_time, "%Y-%m-%d %H:%M:%S")
        diff = current - prev if prev else None
        # Check if we are starting a session
        if log.url.startswith(url_prefix) and not start:
            start = current
            cur_session = 0
            
        # Check if we are within a session.
        elif start and prev:
            diff = current - prev
            if log.url.startswith(url_prefix) and diff.total_seconds() < (60 * 30):
                # Append to current session.
                cur_session += diff.total_seconds()
            elif diff.total_seconds() >= (60 * 30):
                # Break in session.  Close the previous and start a new one.
                if cur_session == 0:
                    # Assume user spent a minute.
                    cur_session = 60
                    
                total += cur_session
                cur_session = 0
                if log.url.startswith(url_prefix):
                    start = current
                else:
                    start = None
            else:
                # Person navigated away.  Close the session.
                cur_session += diff.total_seconds()
                if cur_session == 0:
                    # Assume user spent a minute.
                    cur_session = 60
                    
                total += cur_session
                cur_session = 0
                start = None
                
        prev = current 
        
    return total
        
def calculate_admin_time():
    admin_file = open('time_spent_admin.csv', 'w')
    users = User.objects.filter(is_staff=True)
    for user in users:
        logs = MakahikiLog.objects.filter(remote_user=user.username, url__startswith='/admin/activities/activitymember').order_by('request_time')
        answers = logs.filter(request='POST').count()
        sys.stdout.write('Processing %d logs for %s\n' % (logs.count(), user.username))
        if logs.count() > 0:
            # Iterate over the logs and track previous time and time spent.
            prev = datetime.datetime.strptime(logs[0].request_time, "%Y-%m-%d %H:%M:%S")
            cur_session = total = 0
            for log in logs[1:]:
                current = datetime.datetime.strptime(log.request_time, "%Y-%m-%d %H:%M:%S")
                diff = current - prev
                # Start a new interval if 30 minutes have passed.
                if diff.total_seconds() > (60 * 30):
                    if cur_session == 0:
                        total += 60 # Assume they spent a minute viewing a single page.
                    else:
                        total += cur_session
                    cur_session = 0
                else:
                    cur_session += diff.total_seconds()

                prev = current

            # Append any session that was in progress.
            total += cur_session
            admin_file.write('%s,%d,%d\n' % (user.username, total, answers))
        
    admin_file.close()
    
if __name__ == "__main__":
    calculate_user_time()
    calculate_admin_time()
