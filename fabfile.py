import os
import string
import datetime
from fabric.api import sudo, local, run, settings, require

env.project = "makahiki"

env.hosts = []
env.user = "gelee"

@runs_once
def production():
    """The production server."""
    env.remote_app_dir = "/Users/gelee/Documents/makahiki/"
    env.hosts.append("dasha.ics.hawaii.edu")

def update():
    """Update the latest copy on the server."""
    with cd(env.remote_app_dir):
        run("workon pinax-0.7.2")
        run("git pull origin master")
        run("cp settings.py.example settings.py")
        run("./manage.py migrate")

def reload():
    """Reload apache."""
    with cd(env.remote_app_dir):
        sudo("apachectl graceful")

### Test commands.
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

  
