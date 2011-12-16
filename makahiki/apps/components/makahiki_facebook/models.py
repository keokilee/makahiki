from django.db import models
from django.contrib.auth.models import User

import components.makahiki_facebook.facebook as facebook

# Create your models here.

class FacebookProfile(models.Model):
  about = models.TextField(null=True, blank=True)
  last_name = models.CharField(max_length=255, null=True, blank=True)
  first_name = models.CharField(max_length=255, null=True, blank=True)
  name = models.CharField(max_length=255, null=True, blank=True)
  gender = models.CharField(max_length=255, null=True, blank=True)
  profile_link = models.URLField()
  profile_id = models.BigIntegerField()
  user = models.OneToOneField(User)
  can_post = models.BooleanField(default=False)
  
  @staticmethod
  def create_or_update_from_fb_user(user, fb_user):
    """
    Saves the data retrieved by the cookie so that the we don't need to 
    constantly retrieve data from Facebook. Returns None if the user 
    cannot be retrieved.
    """
    
    if not user or not fb_user:
      return None
      
    try:
      graph = facebook.GraphAPI(fb_user["access_token"])
      graph_profile = graph.get_object("me")
    except facebook.GraphAPIError:
      return None
    
    fb_profile = None
    try:
      fb_profile = user.facebookprofile
    except FacebookProfile.DoesNotExist:
      fb_profile = FacebookProfile(user=user)
      
    for key in graph_profile.keys():
      value = graph_profile[key]
      
      if key == "about":
        fb_profile.about = value
      elif key == "last_name":
        fb_profile.last_name = value
      elif key == "first_name":
        fb_profile.first_name = value
      elif key == "name":
        fb_profile.name = value
      elif key == "gender":
        fb_profile.gender = value
      elif key == "link":
        fb_profile.profile_link = value
      elif key == "id":
        fb_profile.profile_id = value
      
    fb_profile.save()
    return fb_profile