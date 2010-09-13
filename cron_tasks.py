#!/usr/bin/env python

# this script needs to be executed using the virtualenv.
# i.e. Cron should execute "/path/to/virtualenv/bin/python cron_tasks.py"

# Boilerplate setup code from manage.py.
import sys, datetime

from os.path import abspath, dirname, join

from django.conf import settings
from django.core.management import setup_environ

import settings as settings_mod # Assumed to be in the same directory.

# setup the environment before we start accessing things in the settings.
setup_environ(settings_mod)

sys.path.insert(0, join(settings.PINAX_ROOT, "apps"))
sys.path.insert(0, join(settings.PROJECT_ROOT, "apps"))

# Goals

from goals import generate_floor_goals

generate_floor_goals()
    