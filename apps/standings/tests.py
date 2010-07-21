"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from standings import get_standings_for_user, StandingsException
from django.contrib.auth.models import User
    
class UserStandingsTest(TestCase):
  fixtures = ["base_data.json", "user_data.json"]
  
