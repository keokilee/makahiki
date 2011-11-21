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

from components.analytics.models import MakahikiLog
from components.makahiki_profiles.models import ScoreboardEntry, Profile

def raffle_allocation():
    raffle_file = open('raffle_allocation.csv', 'w')
    logs = MakahikiLog.objects.filter(url__startswith='/prizes/raffle/')
    hours = {}
    for log in logs:
        timestamp = datetime.datetime.strptime(log.request_time, "%Y-%m-%d %H:%M:%S")
        date = timestamp.strftime('%m/%d')
        hours[date] = hours.get(date, {})
        hours[date][timestamp.hour] = hours[date].get(timestamp.hour, {})
        if log.url.endswith('add_ticket/'):
            hours[date][timestamp.hour]['add'] = hours[date][timestamp.hour].get('add', 0) + 1
        elif log.url.endswith('remove_ticket/'):
            hours[date][timestamp.hour]['remove'] = hours[date][timestamp.hour].get('remove', 0) + 1
        
    for date, contents in hours.iteritems():
        for hour, info in contents.iteritems():
            raffle_file.write('%s %d:00,%d,%d\n' % (date, hour, info.get('add', 0), info.get('remove', 0)))
    
    raffle_file.close()
    
def raffle_users():
    users = User.objects.filter(profile__points__gte=25, is_staff=False)
    raffle_file = open('raffle_users.csv', 'w')
    for user in users:
        r1_tickets = user.raffleticket_set.filter(raffle_prize__deadline__round_name='Round 1').count()
        r2_tickets = user.raffleticket_set.filter(raffle_prize__deadline__round_name='Round 2').count()
        overall_tickets = user.raffleticket_set.filter(raffle_prize__deadline__round_name='Overall').count()
        r1_points = ScoreboardEntry.objects.get(profile__user=user, round_name='Round 1').points
        r1_unused = max((r1_points / 25) - r1_tickets, 0)
        r2_points = ScoreboardEntry.objects.get(profile__user=user, round_name='Round 2').points
        r2_unused = max(((r1_points + r2_points) / 25) + r1_unused - r2_tickets, 0)
        overall_unused = max((Profile.objects.get(user=user).points / 25) - r1_tickets - r2_tickets - overall_tickets, 0)
        
        raffle_file.write('%s,%d,%d,%d,%d,%d,%d\n' % (user.username, r1_tickets, r1_unused, r2_tickets, r2_unused, overall_tickets, overall_unused))
        
    raffle_file.close()
        
if __name__ == "__main__":
    # raffle_allocation()
    raffle_users()
