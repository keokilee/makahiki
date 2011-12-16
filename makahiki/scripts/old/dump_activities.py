import string
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
import datetime
import settings

setup_environ(settings)

import sys
from os.path import join

sys.path.insert(0, join(settings.PINAX_ROOT, "apps"))
sys.path.insert(0, join(settings.PROJECT_ROOT, "apps"))

from activities.models import Activity, Commitment

# Dump activities
print "title,description,category,duration,points,points_start,points_end"
for activity in Activity.objects.all():
  out_str = "%s,%s," % (activity.title, "\"" + activity.description  + "\"")
  if activity.category:
    out_str += activity.category.name + ","
  else:
    out_str += "None,"
    
  out_str += "%d," % activity.duration
  
  if activity.point_value:
    out_str += "%d," % activity.point_value
  else:
    out_str += "None,"
    
  if activity.point_range_start:
    out_str += "%d," % activity.point_range_start
  else:
    out_str += "None,"
    
  if activity.point_range_end:
    out_str += "%d" % activity.point_range_end
  else:
    out_str += "None"
  print out_str
                         
print ""

# Dump commitments
print "title,description,category,points"
format_string = "%s,%s,%s,%d"
for commitment in Commitment.objects.all():
  category_name = "None"
  if commitment.category:
    category_name = commitment.category.name
    
  print format_string % (commitment.title, "\"" +  commitment.description  + "\"", category_name, commitment.point_value)