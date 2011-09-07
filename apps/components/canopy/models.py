from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from components.activities.models import ActivityBase, ActivityMember

# Create your models here.
class Mission(models.Model):
  name = models.CharField(max_length=255, help_text="Title of the mission.")
  slug = models.SlugField(help_text="Automatically generated in the admin.")
  description = models.TextField(help_text="Description of the mission.")
  is_group = models.BooleanField(default=False, 
      verbose_name="Group Mission", 
      help_text="Check this box if this is a group mission."
  )
  users = models.ManyToManyField(User, through='MissionMember', editable=False)
  activities = models.ManyToManyField(ActivityBase, related_name="missionactivities")
  created_at = models.DateTimeField(auto_now_add=True, editable=False)
  updated_at = models.DateTimeField(auto_now=True, editable=False)
  
  def __unicode__(self):
    return self.name
  
class MissionMember(models.Model):
  user = models.ForeignKey(User)
  mission = models.ForeignKey(Mission)
  completed = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True, editable=False)
  updated_at = models.DateTimeField(auto_now=True, editable=False)
  
  class Meta:
    unique_together = ("user", "mission")
    
  def check_completed(self):
    for activity in self.mission.activities.all():
      try:
        member = ActivityMember.objects.get(
            user=self.user,
            activity=activity,
            approval_status="approved"
        )
      except ActivityMember.DoesNotExist:
        return False
        
    return True
  
@receiver(post_save, sender=ActivityMember)
def mission_activity_handler(sender, instance=None, **kwargs):
  """
  Signal handler for ActivityMembers to see if we completed any missions.
  This is to be triggered when the ActivityMember finishes it's save.
  """
  # Check if we need to handle the instance.
  if not instance:
    return
  if not instance.approval_status == "approved":
    return
    
  members = MissionMember.objects.filter(
      mission__activities__pk=instance.activity.id,
      user=instance.user,
      completed=False,
  )
  if members.count() > 0:
    for member in members:
      if member.check_completed():
        member.completed = True
        member.save()
      
class Post(models.Model):
  user = models.ForeignKey(User, related_name="canopyposts")
  text = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True, editable=False)

