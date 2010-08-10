import os
import string
import datetime
from fabric.api import local, run, settings, require

### Deployment commands.

def local():
  """Sets up the local environment."""
  settings.hosts = ["localhost"]
  settings.user = "gelee"
  settings.staging = "/Users/gelee/Sites/makahiki-staging/"
  settings.production = "/Users/gelee/Sites/makahiki-production/"
  
def remote():
  settings.hosts = ["dasha.ics.hawaii.edu"]
  settings.user = "gelee"

def deploy_staging():
  """Deploys the latest branch to the staging server."""
  require('hosts', provided_by=["local", "remote"])
  settings.path = settings.staging
  settings.release = datetime.datetime.strftime('%Y%m%d%H%M%S')
  
  # Staging uses the current master branch.
  _upload_tar_from_git()
  _update_settings()
  _restart_webserver()
  
def deploy_production():
  require("hosts", provided_by=["local", "remote"])
  settings.release = datetime.datetime.strftime('%Y%m%d%H%M%S')
  settings.path = settings.production + "current/"
  
  # Move staging over to production.
  _move_from_staging()
  _symlink_current_release()
  _update_settings()
  _restart_webserver()
  
def _upload_tar_from_git():
  require("staging", provided_by=["local"])
  require("release", provided_by=["deploy_staging", "deploy_production"])
  
  local('git archive --format=tar master | gzip > $(release).tar.gz')
  put("$(release).tar.gz", "$(staging)")
  run("cd $(staging) && tar -zxf $(release).tar.gz; rm $(release).tar.gz")
  local("rm $(release).tar.gz")
  
def _move_from_staging():
  require("production", provided_by=["local"])
  require("staging")
  require("release", provided_by=["deploy_staging", "deploy_production"])
  
  run("cd $(staging) && tar -cvzf $(release).tar.gz *")
  run("mkdir $(production)/releases/$(release)")
  run("cd $(production)/releases/$(release); tar -zxf ../../$(release).tar.gz; rm ../../$(release).tar.gz")
  
def _symlink_current_release():
    "Symlink our current release"
    
    require("production", provided_by=["local"])
    require('release', provided_by=[deploy_production])
    run('cd $(production); ln -s releases/$(release) current')
    
def _update_settings():
  """Updates the requirements, copies the settings, and migrates the database."""
  require("path", provided_by=["deploy_staging", "deploy_production"])
  
  run('cd $(path); pip install -E . -r requirements.txt')
  run("cd $(path); cp settings.py.example settings.py")
  run("cd $(path); python manage.py syncdb --noinput; python manage.py migrate")
  
def _restart_webserver():
    "Restart the web server"
    sudo('apachectl graceful')

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

  
