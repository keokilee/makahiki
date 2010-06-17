import random
import string
from django.db import IntegrityError

def generate_floors():
  from floors.models import Dorm, Floor
  dorms = Dorm.objects.all()
  floors = ["3-4", "5-6", "7-8", "9-10", "11-12"]
  for dorm in dorms:
     for floor in floors:
       dorm_floor = Floor(number=floor, dorm=dorm)
       dorm_floor.save()


def generate_names():
  from django.contrib.auth.models import User
  from floors.models import Floor

  names = ["alana", "maile", "makani", "kalena", "ikaika", "pono", "kanani", "kanoe", "kahea", "kawika", "makena", "keoni", "keoki", "anuhea", "kealii"]
  initials = "abcdefghijklmnopqrstuvwxyz"
  floors = Floor.objects.all()

  for i in range(0, 600):
    user = None
    while not user:
      try:
        username = string.join(random.sample(names, 1) + random.sample(initials, 1), "")
        user = User(username=username)
        user.save()
      except IntegrityError:
        user = None

    profile = user.get_profile()
    profile.name = user.username[0: len(user.username) - 1].capitalize()
    profile.floor = random.sample(floors, 1)[0]
  
    profile.save()
  
generate_names()
    