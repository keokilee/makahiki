import string
from fabric.api import local

unit_tests = ["activities.tests", "makahiki_base", "standings", "makahiki_profiles.tests"]
selenium_tests = ["activities"]

def run_all_tests_with_report():
  """Runs all of the tests and generates a report."""
  command = "python manage.py test " + string.join(unit_tests + selenium_tests, " ") + " --with-selenium --with-xunit"
  result = local(command, capture=False)
  
def run_tests():
  """Runs all of the tests and does not append a report."""
  command = "python manage.py test " + string.join(unit_tests + selenium_tests, " ") + " --with-selenium"
  result = local(command, capture=False)
  
def push_master():
  local("git checkout master")
  run_tests()
  local("git push origin master")