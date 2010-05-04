import os

items = os.listdir("apps/")
command = "python manage.py test"
print "**Executing the following tests: **"
for item in items:
  if os.path.isdir("apps/" + item):
    print item
    command += " " + item
  
os.system(command)

# testapps = ["basic_profiles"]
# command = "python manage.py test"
# print "**Executing the following tests: **"
# for app in testapps:
#   print app
#   command += " " + app
# 
# os.system(command)