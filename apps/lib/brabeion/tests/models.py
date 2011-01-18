from django.contrib.auth.models import User, UserManager
from django.db import models

from django.contrib.contenttypes import generic

from brabeion.models import BadgeAward

class MyUser(User):
    badges_earned = generic.GenericRelation(BadgeAward)

    # Use UserManager to get the create_user method, etc.
    objects = UserManager()

class PlayerStat(models.Model):
    user = models.OneToOneField(User, related_name="stats")
    points = models.IntegerField(default=0)
