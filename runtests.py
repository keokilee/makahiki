#!/usr/bin/env python

import os
import sys
import string

if len(sys.argv) == 1:
  print "**Running all tests.**"
  apps = [app for app in os.listdir("apps") if os.path.isdir(os.path.join("apps", app))]
  command = "python manage.py test "
  for app in apps:
    if "tests.py" in os.listdir(os.path.join("apps", app)):
      command += "%s.tests " % app
      
    if "selenium" in os.listdir(os.path.join("apps", app)):
      command += "%s.selenium " % app
      
  print "Executing command '" + command + "'"
  os.system(command + "--with-selenium")
  
elif ("unit" in sys.argv) or ("selenium" in sys.argv):
  if "unit" in sys.argv:
    print "**Running Unit and Functional tests**"
    apps = [app for app in os.listdir("apps") if os.path.isdir(os.path.join("apps", app))]
    command = "python manage.py test "
    for app in apps:
      if "tests.py" in os.listdir(os.path.join("apps", app)):
        command += "%s.tests " % app
    os.system(command)

  if "selenium" in sys.argv:
    print "**Running Selenium tests**"
    apps = [app for app in os.listdir("apps") if os.path.isdir(os.path.join("apps", app))]
    command = "python manage.py test "
    for app in apps:
      if "selenium" in os.listdir(os.path.join("apps", app)):
        command += "%s.selenium " % app
        
    os.system(command + "--with-selenium")
    
else:
  print "Usage: python runtests.py [unit] [selenium]"
  


