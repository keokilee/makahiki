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
    
def generate_from_csdl():
  from makahiki_avatar.models import Avatar
  from django.contrib.auth.models import User
  from floors.models import Floor
  avatar_base = "avatars/sample/"

  members = {
    "danport": {"name": "Dan Port", "avatar": "danport.jpg"},
    "kagawaa": {"name": "Aaron Kagawa", "avatar": "aaronkagawa.jpeg"},
    "alexey": {"name": "Alexey Olkov", "avatar": "alexey.jpg"},
    "anned": {"name": "Anne Disney", "avatar": "annedisney.jpeg"},
    "austen": {"name": "Austen Ito", "avatar": "austen.jpg"},
    "carleton": {"name": "Carleton Moore", "avatar": "carleton.jpg"},
    "cedric": {"name": "Cedric Zhang", "avatar": "cedric.jpeg"},
    "christoph": {"name": "Christoph Lofi", "avatar": "christoph.jpg"},
    "dadong": {"name": "Dadong Wan", "avatar": "dadong.png"},
    "danu": {"name": "Danu Tjahjono", "avatar": "danu.png"},
    "dnickels": {"name": "David Nickels", "avatar": "davidnickels.jpg"},
    "hongbing": {"name": "Hongbing Kou", "avatar": "hongbing.jpeg"},
    "jameswang": {"name": "James Wang", "avatar": "jameswang.jpg"},
    "corbett": {"name": "Jay Corbett", "avatar": "jaycorbett.jpeg"},
    "jgeis": {"name": "Jennifer Geis", "avatar": "jennifergeis.jpeg"},
    "jitender": {"name": "Jitender Miglani", "avatar": "jitender.jpeg"},
    "jaugustin": {"name": "Joy Augustin", "avatar": "joyaugustin.jpeg"},
    "jsakuda": {"name": "Julie Sakuda", "avatar": "julie.jpg"},
    "julio": {"name": "Julio Polo", "avatar": "juliopolo.jpeg"},
    "kyleung": {"name": "Ka Yee Leung", "avatar": "kayeeleung.jpeg"},
    "mette": {"name": "Mette Moffett", "avatar": "mette.jpeg"},
    "staver": {"name": "Michael Staver", "avatar": "michaelstaver.jpeg"},
    "paulding": {"name": "Mike Paulding", "avatar": "mikepaulding.jpg"},
    "monir": {"name": "Monir Hodges", "avatar": "monir.jpeg"},
    "pavel": {"name": "Pavel Senin", "avatar": "pavel.jpg"},
    "randycox": {"name": "Randy Cox", "avatar": "randycox.jpeg"},
    "rosemary": {"name": "Rosemary Andrada Sumajit", "avatar": "rosemary.png"},
    "russell": {"name": "Russell Tokuyama", "avatar": "russell.jpeg"},
    "joedane": {"name": "Joe Dane", "avatar": "joedane.jpeg"}
  }

  initials = "abcdefghijklmnopqrstuvwxyz"
  floors = Floor.objects.all()
  
  for i in range(0, 600):
    user = None
    while not user:
      try:
        username = string.join(random.sample(members.keys(), 1) + random.sample(initials, 1), "")
        user = User(username=username)
        user.save()
      except IntegrityError:
        user = None

    key = user.username[0: len(user.username) - 1]
    profile = user.get_profile()
    profile.name = members[key]["name"]
    profile.floor = random.sample(floors, 1)[0]
    profile.save()

    avatar_path = avatar_base + members[key]["avatar"]
    avatar = Avatar(user=user, primary=True, avatar=avatar_path)
    avatar.save()
    
def generate_csdl_for_floor(floor):
  from makahiki_avatar.models import Avatar
  from django.contrib.auth.models import User
  from floors.models import Floor
  avatar_base = "avatars/sample/"

  members = {
    "danport": {"name": "Dan Port", "avatar": "danport.jpg"},
    "kagawaa": {"name": "Aaron Kagawa", "avatar": "aaronkagawa.jpeg"},
    "alexey": {"name": "Alexey Olkov", "avatar": "alexey.jpg"},
    "anned": {"name": "Anne Disney", "avatar": "annedisney.jpeg"},
    "austen": {"name": "Austen Ito", "avatar": "austen.jpg"},
    "carleton": {"name": "Carleton Moore", "avatar": "carleton.jpeg"},
    "cedric": {"name": "Cedric Zhang", "avatar": "cedric.jpeg"},
    "christoph": {"name": "Christoph Lofi", "avatar": "christoph.jpg"},
    "dadong": {"name": "Dadong Wan", "avatar": "dadong.png"},
    "danu": {"name": "Danu Tjahjono", "avatar": "danu.png"},
    "dnickels": {"name": "David Nickels", "avatar": "davidnickels.jpg"},
    "hongbing": {"name": "Hongbing Kou", "avatar": "hongbing.jpeg"},
    "jameswang": {"name": "James Wang", "avatar": "jameswang.jpg"},
    "corbett": {"name": "Jay Corbett", "avatar": "jaycorbett.jpeg"},
    "jgeis": {"name": "Jennifer Geis", "avatar": "jennifergeis.jpeg"},
    "jitender": {"name": "Jitender Miglani", "avatar": "jitender.jpeg"},
    "jaugustin": {"name": "Joy Augustin", "avatar": "joyaugustin.jpeg"},
    "jsakuda": {"name": "Julie Sakuda", "avatar": "julie.jpg"},
    "julio": {"name": "Julio Polo", "avatar": "juliopolo.jpeg"},
    "kyleung": {"name": "Ka Yee Leung", "avatar": "kayeeleung.jpeg"},
    "mette": {"name": "Mette Moffett", "avatar": "mette.jpeg"},
    "staver": {"name": "Michael Staver", "avatar": "michaelstaver.jpeg"},
    "paulding": {"name": "Mike Paulding", "avatar": "mikepaulding.jpg"},
    "monir": {"name": "Monir Hodges", "avatar": "monir.jpeg"},
    "pavel": {"name": "Pavel Senin", "avatar": "pavel.jpg"},
    "randycox": {"name": "Randy Cox", "avatar": "randycox.jpeg"},
    "rosemary": {"name": "Rosemary Andrada Sumajit", "avatar": "rosemary.png"},
    "russell": {"name": "Russell Tokuyama", "avatar": "russell.jpeg"},
    "joedane": {"name": "Joe Dane", "avatar": "joedane.jpeg"}
  }

  for key in members.keys():
    user = None
    try:
      user = User(username=key)
      user.save()
    except IntegrityError:
      print "Integrity Error: Duplicate user."
      exit()

    profile = user.get_profile()
    profile.name = members[key]["name"]
    profile.floor = floor
    profile.save()

    avatar_path = avatar_base + members[key]["avatar"]
    avatar = Avatar(user=user, primary=True, avatar=avatar_path)
    avatar.save()