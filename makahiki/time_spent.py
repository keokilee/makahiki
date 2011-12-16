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

MIN_SESSION = 60 # Assume user spends 60 seconds on a single page.

USER_HEADER = 'user id,total seconds spent,home seconds spent,activities seconds spent,energy seconds spent,prizes seconds spent,news seconds spent,profile seconds spent,help seconds spent,canopy seconds spent\n'
LOUNGE_HEADER = 'lounge,total seconds spent,home seconds spent,activities seconds spent,energy seconds spent,prizes seconds spent,news seconds spent,profile seconds spent,help seconds spent,canopy seconds spent\n'

DAYS_HEADER = 'user id, total days visited, home days visited, activities days visited, energy days visited, prizes days visited, news days visited, profile days visited, help days visited, canopy days visited\n'

SESSION_HEADER = 'user id,a_21_visits_0-5,a_22_visits_5-10,a_23_visits_10-15,a_24_visits_15-30,a_25_visits_30-60,a_26_visits_60+\n'

def calculate_days_spent():
    users_file = open('days_spent.csv', 'w')
    users = User.objects.filter(profile__points__gt=0, profile__floor__isnull=False).order_by('-profile__points', 'id')
    counter = 1
    user_count = users.count()
    users_file.write(DAYS_HEADER)
    start_date = datetime.datetime(2011, 10, 17).strftime("%Y-%m-%d %H:%M:%S")
    end_date = datetime.datetime(2011, 11, 7).strftime("%Y-%m-%d %H:%M:%S")
    
    for user in users:
        logs = MakahikiLog.objects.filter(remote_user=user.username, request_time__lt=end_date, request_time__gt=start_date).order_by('request_time')
        sys.stdout.write('Processing %d logs for %s (%d/%d)\n' % (logs.count(), user.username, counter, user_count))
        days = _days_spent(logs)
        home = _days_spent(logs, path='/home')
        activities = _days_spent(logs, path='/activities')
        energy = _days_spent(logs, path='/energy')
        prizes = _days_spent(logs, path='/prizes')
        news = _days_spent(logs, path='/news')
        profile = _days_spent(logs, path='/profile')
        help = _days_spent(logs, path='/help')
        canopy = _days_spent(logs, path='/canopy')
        
        contents = '%d,%d,%d,%d,%d,%d,%d,%d,%d,%d\n' % (user.id, days, home, activities, energy, prizes, news, profile, help, canopy)
        sys.stdout.write('contents ' + contents)
        users_file.write(contents)
        counter += 1
        
    users_file.close()
    
def calculate_sessions():
    users_file = open('sessions.csv', 'w')
    users = User.objects.filter(profile__points__gt=0, profile__floor__isnull=False).order_by('-profile__points', 'id')
    counter = 1
    user_count = users.count()
    users_file.write(SESSION_HEADER)
    start_date = datetime.datetime(2011, 10, 17).strftime("%Y-%m-%d %H:%M:%S")
    end_date = datetime.datetime(2011, 11, 7).strftime("%Y-%m-%d %H:%M:%S")
    
    for user in users:
        logs = MakahikiLog.objects.filter(
                remote_user=user.username, 
                request_time__lt=end_date, 
                request_time__gt=start_date
        ).order_by('request_time')
        
        sys.stdout.write('Processing %d logs for %s (%d/%d)\n' % (logs.count(), user.username, counter, user_count))
        sessions = _sessions(logs)
        
        contents = '%d,%d,%d,%d,%d,%d,%d\n' % (
                user.id,
                sessions.get('0-5', 0),
                sessions.get('5-10', 0),
                sessions.get('10-15', 0),
                sessions.get('15-30', 0),
                sessions.get('30-60', 0),
                sessions.get('60+', 0)
        )
        sys.stdout.write('contents ' + contents)
        users_file.write(contents)
        counter += 1
        
    users_file.close()
    
    
def calculate_user_time():
    users_file = open('time_spent_users.csv', 'w')
    lounge_file = open('time_spent_lounge.csv', 'w')
    users = User.objects.filter(profile__points__gt=0, profile__floor__isnull=False).order_by('-profile__points', 'id')
    lounges = {}
    counter = 1
    user_count = users.count()
    users_file.write(USER_HEADER)
    lounge_file.write(LOUNGE_HEADER)
    
    for user in users:
        logs = MakahikiLog.objects.filter(remote_user=user.username).order_by('request_time')
        sys.stdout.write('Processing %d logs for %s (%d/%d)\n' % (logs.count(), user.username, counter, user_count))
        total = _time_spent(logs)
        home_time = _page_time('/home', logs)
        activity_time = _page_time('/activities', logs)
        energy_time = _page_time('/energy', logs)
        prize_time = _page_time('/prizes', logs)
        news_time = _page_time('/news', logs)
        profile_time = _page_time('/profile', logs)
        help_time = _page_time('/help', logs)
        canopy_time = _page_time('/canopy', logs)
        
        users_file.write('%d,%d,%d,%d,%d,%d,%d,%d,%d,%d\n' % (user.id, total, home_time, activity_time, energy_time, 
                prize_time, news_time, profile_time, help_time, canopy_time))
        lounge = str(user.get_profile().floor)
        lounges[lounge] = lounges.get(lounge, {})
        lounges[lounge]['total'] = lounges[lounge].get('total', 0) + total
        lounges[lounge]['home'] = lounges[lounge].get('home', 0) + home_time
        lounges[lounge]['activities'] = lounges[lounge].get('activities', 0) + activity_time
        lounges[lounge]['energy'] = lounges[lounge].get('energy', 0) + energy_time
        lounges[lounge]['prizes'] = lounges[lounge].get('prizes', 0) + prize_time
        lounges[lounge]['news'] = lounges[lounge].get('news', 0) + news_time
        lounges[lounge]['profile'] = lounges[lounge].get('profile', 0) + profile_time
        lounges[lounge]['help'] = lounges[lounge].get('help', 0) + help_time
        lounges[lounge]['canopy'] = lounges[lounge].get('canopy', 0) + canopy_time
        counter += 1
        
    for lounge, items in lounges.iteritems():
        lounge_file.write('%s,%d,%d,%d,%d,%d,%d,%d,%d,%d\n' % (lounge, items['total'], items['home'], items['activities'], 
                items['energy'], items['prizes'], items['news'], items['profile'], items['help'], items['canopy']))
        
    lounge_file.close()
    users_file.close()
    
def _time_spent(logs, start_date=None):
    # Iterate over the logs and track previous time and time spent.
    query = logs
    if start_date:
        query = query.filter(request_time__gt=start_date)
    
    if query.count() > 0:
        prev = datetime.datetime.strptime(query[0].request_time, "%Y-%m-%d %H:%M:%S")
        cur_session = total = 0
        for log in query[1:]:
            current = datetime.datetime.strptime(log.request_time, "%Y-%m-%d %H:%M:%S")
            diff = current - prev
            # Start a new interval if 30 minutes have passed.
            if diff.total_seconds() > (60 * 30):
                if cur_session == 0:
                    total += MIN_SESSION
                else:
                    total += cur_session
                cur_session = 0
            else:
                cur_session += diff.total_seconds()

            prev = current

        # Append any session that was in progress.
        total += cur_session
        return total
    
    return 0
    
def _days_spent(logs, path=None, start_date=None):
    query = logs
    if start_date:
        query = query.filter(request_time__gt=start_date)
    if path:
        query = query.filter(url__startswith=path)
    
    # Iterate over the logs and track current date and days.
    days = 0
    cur_date = None
    for log in query:
        # Only concerned with the date portion of the timestamp.
        date = datetime.datetime.strptime(log.request_time, "%Y-%m-%d %H:%M:%S").date()
        if not cur_date:
            cur_date = date
            days += 1
        elif cur_date < date:
            cur_date = date
            days += 1
        
    return days
    
def _sessions(logs, start_date=None):
    return_dict = {}
    
    # Iterate over the logs and track previous time and time spent.
    query = logs
    if start_date:
        query = query.filter(request_time__gt=start_date)
    
    if query.count() > 0:
        prev = datetime.datetime.strptime(query[0].request_time, "%Y-%m-%d %H:%M:%S")
        cur_session = total = 0
        for log in query[1:]:
            current = datetime.datetime.strptime(log.request_time, "%Y-%m-%d %H:%M:%S")
            diff = current - prev
            # Start a new interval if 30 minutes have passed.
            if diff.total_seconds() > (60 * 30):
                if cur_session == 0:
                    minutes = MIN_SESSION / 60
                else:
                    minutes = cur_session / 60
                    
                if minutes > 60:
                    return_dict['60+'] = return_dict.get('60+', 0) + 1
                elif minutes > 30:
                    return_dict['30-60'] = return_dict.get('30-60', 0) + 1
                elif minutes > 15:
                    return_dict['15-30'] = return_dict.get('15-30', 0) + 1
                elif minutes > 10:
                    return_dict['10-15'] = return_dict.get('10-15', 0) + 1
                elif minutes > 5:
                    return_dict['5-10'] = return_dict.get('5-10', 0) + 1
                else:
                    return_dict['0-5'] = return_dict.get('0-5', 0) + 1
                    
                cur_session = 0
            else:
                cur_session += diff.total_seconds()

            prev = current

        # Append any session that was in progress.
        if cur_session == 0:
            minutes = MIN_SESSION / 60
        else:
            minutes = cur_session / 60
            
        if minutes > 60:
            return_dict['60+'] = return_dict.get('60+', 0) + 1
        elif minutes > 30:
            return_dict['30-60'] = return_dict.get('30-60', 0) + 1
        elif minutes > 15:
            return_dict['15-30'] = return_dict.get('15-30', 0) + 1
        elif minutes > 10:
            return_dict['10-15'] = return_dict.get('10-15', 0) + 1
        elif minutes > 5:
            return_dict['5-10'] = return_dict.get('5-10', 0) + 1
        else:
            return_dict['0-5'] = return_dict.get('0-5', 0) + 1
    
    return return_dict
    
def _page_time(url_prefix, logs, start_date=None):
    start = prev = None
    total = cur_session = 0
    # Need to filter out AJAX interactions.
    query = logs.exclude(Q(url__startswith='/log') | Q(url__startswith='/slog') | Q(url__startswith='/notifications') | Q(url__startswith='/quests'))
    if start_date:
        query = logs.filter(request_time__gt=start_date)
    for log in query:
        current = datetime.datetime.strptime(log.request_time, "%Y-%m-%d %H:%M:%S")
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
                    cur_session = MIN_SESSION
                    
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
                    cur_session = MIN_SESSION
                    
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
    
def calculate_canopy_time():
    users = User.objects.filter(profile__canopy_member=True, is_staff=False)
    canopy_date = '2011-10-31 17:50:40' # Time last canopy notification went out.
    for user in users:
        logs = MakahikiLog.objects.filter(remote_user=user.username).order_by('request_time')
        total_time = _time_spent(logs, start_date=canopy_date)
        canopy_time = _page_time('/canopy', logs, start_date=canopy_date)
        print '%d,%d,%d' % (user.id, canopy_time, total_time)
        
if __name__ == "__main__":
    calculate_user_time()
    # calculate_admin_time()
    # calculate_canopy_time()
    # calculate_days_spent()
    # calculate_sessions()