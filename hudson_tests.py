#!/usr/bin/env python

import os
import subprocess
import signal

# Prepare settings.
print "**Initializing settings**"
files = os.listdir(".")
if "settings.py" not in files:
  print "**Using example settings.**"
  os.system("cp settings.py.example settings.py")
if "local_settings.py" in files:
  print "**Backing up local_settings**"
  os.system("cp local_settings.py local_settings.py.temp")

print "**Preparing test settings**"
os.system("cp local_settings.py.test local_settings.py")
  
print "**Setting up the database.**"
# Database is created, so we need to run migrations.
os.system("python manage.py migrate")
# Reload fixtures.
os.system("python manage.py loaddata fixtures/base_data.json fixtures/user_data.json")

print "**Initializing webserver.**"
# Start the web server in the background.
os.system("python manage.py runserver -v 0 --noreload 8105 &")

print "**Running runtests.py**"
os.system("python runtests.py")

print "**Terminating web server**"
# Find the pid of the runserver task.
tasks = subprocess.Popen("ps x | grep 'python manage.py runserver -v 0 --noreload 8105'", shell=True, stdout=subprocess.PIPE)
task_rows = tasks.stdout.read().split("\n")
for task in task_rows:
  if task.find("manage.py") > 0:
    os.kill(int(task.split()[0]), signal.SIGTERM)
    break
      


print "**Cleaning up test database."
os.system("python manage.py reset activities makahiki_base django_generic_flatblocks gblocks --noinput")
os.system("python manage.py reset auth makahiki_profiles makahiki_avatar floors --noinput")

print "**Removing test settings.**"
os.system("rm local_settings.py")

files = os.listdir(".")
if "local_settings.py.temp" in files:
  print "**Restoring local_settings**"
  os.system("mv local_settings.py.temp local_settings.py")

  


