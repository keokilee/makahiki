from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models import Q

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
  activities = models.ManyToManyField(ActivityBase)
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
    
  def save(self, *args, **kwargs):
    """
    Override for save function to find activity members where this user is specified.
    """
    super(MissionMember, self).save(*args, **kwargs)
    
    # We check this after saving because this process may mark the mission as completed.
    if not self.completed:
      # Find any activity member objects for this mission that reference this user's email.
      # User should not already be participating in this activity.
      members = ActivityMember.objects.filter(
          Q(social_email=self.user.email) | Q(social_email2=self.user.email),
          activity__mission=self.mission,
          approval_status='approved',
      ).exclude(
          user=self.user,
      )
      
      user_activities = self.user.activity_set.all()
      
      for member in members:
        if member.activity not in user_activities:
          new_member = ActivityMember.objects.create(user=self.user, activity=member.activity,)
          new_member.question = member.question
          new_member.response = member.response
          new_member.image = member.image
          new_member.points_awarded = member.points_awarded
          new_member.submission_date = member.submission_date

          new_member.approval_status = 'approved'
          new_member.save()
          
          user_activities = self.user.activity_set.all()
  
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

