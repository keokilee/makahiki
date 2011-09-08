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
    
  def participating_users(self):
    """
    Return the users who are participating in this mission.
    """
    return self.users.filter(
        missionmember__mission=self,
        missionmember__completed=False,
    )
    
  def completed_users(self):
    """
    Return the users who completed this mission.
    """
    return self.users.filter(
        missionmember__mission=self,
        missionmember__completed=True,
    )
    
  def is_completed(self, user):
    """
    Checks if the mission is completed.
    """
    # If this is a group mission, we need to check if the user is a member of the mission.
    if self.is_group and user not in self.users.all():
      return False
      
    for activity in self.activities.all():
      try:
        member = ActivityMember.objects.get(
            user=user,
            activity=activity,
            approval_status="approved",
        )
      except ActivityMember.DoesNotExist:
        return False
        
    return True
  
class MissionMember(models.Model):
  user = models.ForeignKey(User)
  mission = models.ForeignKey(Mission)
  completed = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True, editable=False)
  updated_at = models.DateTimeField(auto_now=True, editable=False)
  
  class Meta:
    unique_together = ("user", "mission")
  
@receiver(post_save, sender=ActivityMember)
def mission_activity_handler(sender, instance=None, **kwargs):
  """
  Signal handler for ActivityMembers to see if we completed any missions.
  This is to be triggered when the ActivityMember finishes its save.
  """
  # Check if we need to handle the instance.
  if not instance:
    return
  if not instance.approval_status == "approved":
    return
  
  # Check completion for all missions that contain this instance's activity
  missions = Mission.objects.filter(
      activities__pk=instance.activity.id,
  )
  
  for mission in missions:
    if mission.is_completed(instance.user):
      member, created = MissionMember.objects.get_or_create(user=instance.user, mission=mission)
      if not member.completed:
        member.completed = True
        member.save()
    
class Post(models.Model):
  user = models.ForeignKey(User, related_name="canopyposts")
  text = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True, editable=False)

