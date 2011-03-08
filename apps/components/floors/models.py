import datetime

from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.db.models import Sum, Max, Q

from components.makahiki_base import get_floor_label, get_current_round

# Create your models here.

class Dorm(models.Model):
  # Automatically populate slug field when the name is added.
  prepopulated_fields = {"slug": ("name",)}
  
  name = models.CharField(max_length=200, help_text="The name of the dorm.")
  slug = models.SlugField(max_length=20, help_text="Automatically generated if left blank.")
  created_at = models.DateTimeField(editable=False);
  updated_at = models.DateTimeField(null=True, editable=False)
  
  def __unicode__(self):
    return self.name
    
  def floor_points_leaders(self, num_results=10, round_name=None):
    """
    Returns the top points leaders for the given dorm.
    """
    if round_name:
      return self.floor_set.filter(
          profile__scoreboardentry__round_name=round_name
      ).annotate(
          points=Sum("profile__scoreboardentry__points"), 
          last=Max("profile__scoreboardentry__last_awarded_submission")
      ).order_by("-points", "-last")[:num_results]
      
    return self.floor_set.annotate(
        points=Sum("profile__points"), 
        last=Max("profile__last_awarded_submission")
    ).order_by("-points", "-last")[:num_results]
    
  def save(self, *args, **kwargs):
    """Custom save method to generate slug and set created_at/updated_at."""
    if not self.slug:
      self.slug = slugify(self.name)
    
    if not self.created_at:
      self.created_at = datetime.date.today()
    else:
      self.updated_at = datetime.date.today()
      
    super(Dorm, self).save()
    
class Floor(models.Model):
  prepopulated_fields = {"slug": ("number",)}
  
  number = models.CharField(help_text="The floor number in the dorm. Can be a string value", max_length=10)
  slug = models.SlugField(max_length=10, help_text="Automatically generated if left blank.")
  dorm = models.ForeignKey(Dorm, help_text="The dorm this floor belongs to.")
  floor_identifier = models.CharField(
      max_length=200,
      blank=True,
      null=True,
      help_text="Name of the variable used in the kukuicup configuration to refer to this floor."
  )
  
  def __unicode__(self):
    return "%s: %s %s" % (self.dorm.name, get_floor_label(), self.number)
    
  @staticmethod
  def floor_points_leaders(num_results=10, round_name=None):
    if round_name:
      return Floor.objects.filter(
          profile__scoreboardentry__round_name=round_name
      ).annotate(
          points=Sum("profile__scoreboardentry__points"), 
          last=Max("profile__scoreboardentry__last_awarded_submission")
      ).order_by("-points", "-last")[:num_results]
      
    return Floor.objects.annotate(
        points=Sum("profile__points"), 
        last=Max("profile__last_awarded_submission")
    ).order_by("-points", "-last")[:num_results]
    
  def points_leaders(self, num_results=10, round_name=None):
    """
    Gets the points leaders for the current floor.
    """
    if round_name:
      return self.profile_set.filter(
          scoreboardentry__round_name=round_name
      ).order_by("-scoreboardentry__points", "-scoreboardentry__last_awarded_submission")[:num_results]
      
    return self.profile_set.all().order_by("-points", "-last_awarded_submission")[:num_results]
    
  def current_round_rank(self):
    round_info = get_current_round()
    if round_info:
      return self.rank(round_name=round_info["title"])

    return None
    
  def rank(self, round_name=None):
    """Returns the rank of the floor across all dorms."""
    if round_name:
      from components.makahiki_profiles.models import ScoreboardEntry
      
      aggregate = ScoreboardEntry.objects.filter(
          profile__floor=self, 
          round_name=round_name
      ).aggregate(points=Sum("points"), last=Max("last_awarded_submission"))
      
      points = aggregate["points"] or 0
      last_awarded_submission = aggregate["last"]
      # Group by floors, filter out other rounds, and annotate.
      annotated_floors = ScoreboardEntry.objects.values("profile__floor").filter(
          round_name=round_name
      ).annotate(
          floor_points=Sum("points"),
          last_awarded=Max("last_awarded_submission")
      )
    else:
      aggregate = self.profile_set.aggregate(points=Sum("points"), last=Max("last_awarded_submission"))
      points = aggregate["points"] or 0
      last_awarded_submission = aggregate["last"]

      annotated_floors = Floor.objects.annotate(
          floor_points=Sum("profile__points"),
          last_awarded_submission=Max("profile__last_awarded_submission")
      )
    
    count = annotated_floors.filter(floor_points__gt=points).count()
    # If there was a submission, tack that on to the count.
    if last_awarded_submission:
      count = count + annotated_floors.filter(
          floor_points=points, 
          last_awarded_submission__gt=last_awarded_submission
      ).count()
      
    return count + 1
    
  def current_round_points(self):
    """Returns the number of points for the current round."""
    round_info = get_current_round()
    if round_info:
      return self.points(round_name=round_info["title"])

    return None
    
  def points(self, round_name=None):
    """Returns the total number of points for the floor.  Takes an optional parameter for a round."""
    if round_name:
      from components.makahiki_profiles.models import ScoreboardEntry
      dictionary = ScoreboardEntry.objects.filter(profile__floor=self, round_name=round_name).aggregate(Sum("points"))
    else:
      dictionary = self.profile_set.aggregate(Sum("points"))
      
    return dictionary["points__sum"] or 0
    
  def save(self):
    """Custom save method to generate slug and set created_at/updated_at."""
    if not self.slug:
      self.slug = slugify(self.number)

    super(Floor, self).save()
    
class Post(models.Model):
  """Represents a wall post on a user's wall."""
  user = models.ForeignKey(User)
  floor = models.ForeignKey(Floor)
  text = models.TextField()
  style_class = models.CharField(max_length=50, default="user_post") #CSS class to apply to this post.
  created_at = models.DateTimeField(editable=False)
  
  def date_string(self):
    """Formats the created date into a pretty string."""
    return self.created_at.strftime("%m/%d %I:%M %p")
  
  def save(self):
    if not self.created_at:
      self.created_at = datetime.datetime.today()
    
    super(Post, self).save()
  
class PostComment(models.Model):
  user = models.ForeignKey(User)
  post = models.ForeignKey(Post)
  text = models.TextField()
  created_at = models.DateTimeField(editable=False)
  
  def save(self):
    if not self.created_at:
      self.created_at = datetime.date.today()
    
    super(PostComment, self).save()