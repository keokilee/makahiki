#!/usr/bin/env python

import os
import sys
import string

unit_tests = ["activities.tests", "makahiki_base", "standings"]
selenium_tests = ["activities"]

if len(sys.argv) == 1:
  print "**Running all tests.**"
  command = "python manage.py test " + string.join(unit_tests + selenium_tests, " ") + " --with-selenium --with-xunit"
  os.system(command)
  
elif ("unit" in sys.argv) or ("selenium" in sys.argv):
  if "unit" in sys.argv:
    print "**Running Unit and Functional tests**"
    command = "python manage.py test " + string.join(unit_tests, " ")
    os.system(command)

  if "selenium" in sys.argv:
    print "**Running Selenium tests**"
    command = "python manage.py test " + string.join(selenium_tests, " ") + " --with-selenium"
    os.system(command)
    
else:
  print "Usage: python runtests.py [unit] [selenium]"
  


