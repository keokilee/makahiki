from django.db import models
from basic_profiles.models import Profile

# Create your models here.
class KukuiCupProfile(Profile):
  points = models.IntegerField()