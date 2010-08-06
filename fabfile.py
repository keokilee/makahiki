import os
import string
from fabric.api import local, run
  
def test_selenium():
  """Runs the selenium tests."""
  
  apps = [app for app in os.listdir("apps") if os.path.isdir(os.path.join("apps", app))]
  command = "python manage.py test "
  for app in apps:
    if "selenium" in os.listdir(os.path.join("apps", app)):
      command += "%s.selenium" % app
      
  result = local(command, capture=False)
  
def test_unit():
  """Runs the unit and functional tests."""

  apps = [app for app in os.listdir("apps") if os.path.isdir(os.path.join("apps", app))]
  command = "python manage.py test "
  for app in apps:
    if "tests.py" in os.listdir(os.path.join("apps", app)):
      command += "%s.tests" % app

  result = local(command, capture=False)
  
def test():
  """Runs the tests with the option to run the automated Selenium tests."""
  
  response = ""
  while response != "yes" and response != "no":
    response = raw_input("Do you want to run the Selenium tests (yes/no)? ")
    
  test_unit()
  if response == "yes":
    print "Running Selenium tests"
    test_selenium()
  
