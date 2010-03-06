import os

testapps = ["basic_profiles", "tribes"]
command = "python manage.py test"
print "**Executing the following tests: **"
for app in testapps:
  print app
  command += " " + app

os.system(command)