import datetime
import random
import string
import os

from django.db import models, IntegrityError
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from components.activities import *
from django.contrib.sites.models import Site
from django.core.cache import cache

# Register badges immediately.
from components.makahiki_badges import user_badges
from lib.brabeion import badges

from components.floors.models import Post
from components.makahiki_base.models import Like
from components.makahiki_notifications.models import UserNotification
from components.cache.utils import invalidate_floor_avatar_cache, invalidate_commitments_cache

MARKDOWN_LINK = "http://daringfireball.net/projects/markdown/syntax"
MARKDOWN_TEXT = "Uses <a href=\"" + MARKDOWN_LINK + "\" target=\"_blank\">Markdown</a> formatting."
    
class Category(models.Model):
  """Categories used to group commitments and activities."""
  name = models.CharField(max_length=255, help_text="255 character maximum")
  slug = models.SlugField(help_text="Automatically generated if left blank.", null=True)

  class Meta:
    verbose_name_plural = "categories"

  def __unicode__(self):
    return self.name

class TextPromptQuestion(models.Model):
  """Represents questions that can be asked of users in order to verify participation in activities."""
  
  activity = models.ForeignKey("Activity")
  question = models.TextField()
  answer = models.CharField(max_length=255, help_text="255 character max.", null=True, blank=True)
  
  def __unicode__(self):
    return "Question: '%s' Answer: '%s'" % (self.question, self.answer)

class QuestionChoice(models.Model):
  """Represents questions's multiple choice"""
  
  question = models.ForeignKey("TextPromptQuestion")
  activity = models.ForeignKey("Activity")
  choice = models.CharField(max_length=255, help_text="255 character max.")
  
  def __unicode__(self):
    return self.choice
    
class ConfirmationCode(models.Model):
  """Represents confirmation codes for activities."""
  activity = models.ForeignKey("Activity")
  code = models.CharField(max_length=50, unique=True, db_index=True)
  is_active = models.BooleanField(default=True, editable=False)
  
  @staticmethod
  def generate_codes_for_activity(activity, num_codes):
    """Generates a set of random codes for the activity."""
    values = 'abcdefghijkmnpqrstuvwxyz234789'
    
    # Use the first non-dash component of the slug.
    components = activity.slug.split('-')
    header = components[0]
    # Need to see if there are other codes with this header.
    index = 1
    while ConfirmationCode.objects.filter(code__istartswith=header).count() > 0 and index < len(components):
      header += components[index]
      index += 1
      
    header += "-"
    for i in range(0, num_codes):
      code = ConfirmationCode(activity=activity, code=header)
      valid = False
      while not valid:
        for value in random.sample(values, 5):
          code.code += value
        try:
          # print code.code
          # Throws exception if the code is a duplicate.
          code.save()
          valid = True
        except IntegrityError:
          # Try again.
          code.code = header
          
# ActivityBase 
class ActivityBase(models.Model):
  TYPE_CHOICES = (
    ('activity', 'Activity'),
    ('commitment', 'Commitment'),
    ('event', 'Event'),
    ('survey', 'Survey'),
    ('excursion', 'Excursion'),
  )
  
  name = models.CharField(max_length=20, null=True)
  slug = models.SlugField(help_text="Automatically generated if left blank.", null=True)
  title = models.CharField(max_length=200)
  description = models.TextField(help_text=MARKDOWN_TEXT)
  type = models.CharField(
                  max_length=20, 
                  choices=TYPE_CHOICES, 
                  verbose_name="Activity Type"
                 )
  category = models.ForeignKey(Category, null=True, blank=True)
  priority = models.IntegerField(
                default=1000,
                help_text="Orders the activities in the available activities list. " + 
                          "Activities with lower values (higher priority) will be listed first."
             )
  likes = generic.GenericRelation(Like)
  depends_on = models.CharField(max_length=400, null=True, blank=True,)
  depends_on_text = models.CharField(max_length=400, null=True, blank=True,)
  energy_related = models.BooleanField(default=False)
  social_bonus = models.IntegerField(default=0, help_text="Social bonus points.")
  mobile_restricted = models.BooleanField(default=False, help_text="Set to true if this task should not be displayed on mobile devices.")

  is_canopy = models.BooleanField(default=False,
      verbose_name="Canopy Activity",
      help_text="Check this box if this is a canopy activity."
  )
  
  is_group = models.BooleanField(default=False, 
      verbose_name="Group Activity",
      help_text="Check this box if this is a group activity."
  )

  created_at = models.DateTimeField(editable=False, auto_now_add=True)
  updated_at = models.DateTimeField(editable=False, auto_now=True, null=True)
  
  def __unicode__(self):
    return "%s: %s" % (self.type.capitalize(), self.title)
    
class Commitment(ActivityBase):
  """Commitments involve non-verifiable actions that a user can commit to.
  Typically, they will be worth fewer points than activities."""
  duration = models.IntegerField(default=5, help_text="Duration of commitment, in days.")
  point_value = models.IntegerField(
                  help_text="Specify a single point value to be awarded."
                ) # This is validated by the admin form.  
  users = models.ManyToManyField(User, through="CommitmentMember")
  
  def __unicode__(self):
    return self.title

  def save(self):
    """Custom save method to set fields."""
    self.type = "commitment"
    super(Commitment, self).save()
    
class Activity(ActivityBase):
  """Activities involve verifiable actions that users commit to.  These actions can be 
  verified by asking questions or posting an image attachment that verifies the user did 
  the activity."""
  
  class Meta:
    verbose_name_plural = "activities"
  
  CONFIRM_CHOICES = (
    ('text', 'Question and Answer'),
    ('image', 'Image Upload'),
    ('code', 'Confirmation Code'),
    ('free', 'Free Response'),
    ('free_image', 'Free Response and Image Upload'),
  )
  
  users = models.ManyToManyField(User, through="ActivityMember")
  duration = models.IntegerField(
              verbose_name="Expected activity duration",
              help_text="Time (in minutes) that the activity is expected to take."
             )
  point_value = models.IntegerField(
                  null=True, 
                  blank=True, 
                  help_text="Specify a single point value or a range of points to be awarded."
                ) # This is validated by the admin form.               
  point_range_start = models.IntegerField(
                        null=True, 
                        blank=True, 
                        help_text="Minimum number of points possible for this activity."
                      )
  point_range_end = models.IntegerField(
                        null=True, 
                        blank=True, 
                        help_text="Maximum number of points possible for this activity."
                      )
  
  pub_date = models.DateField(
              default=datetime.date.today(),
              verbose_name="Publication date",
              help_text="Date at which the activity will be available for users."
             )
  expire_date = models.DateField(
                verbose_name="Expiration date", 
                help_text="Date at which the activity will be removed."
              )
  confirm_type = models.CharField(
                  max_length=20, 
                  choices=CONFIRM_CHOICES, 
                  default="text",
                  verbose_name="Confirmation Type"
                 )
  confirm_prompt = models.TextField(
                    blank=True, 
                    verbose_name="Confirmation prompt",
                    help_text="Text to display to user when requesting points (for images, free response, and codes)."
                   )
  event_date = models.DateTimeField(
                null=True, 
                blank=True, 
                verbose_name="Date and time of the event",
                help_text="Required for events."
               )
  event_location = models.CharField(
                    blank=True,
                    null=True,
                    max_length=200, 
                    verbose_name="Event Location",
                    help_text="Location of the event"
                )
  event_max_seat = models.IntegerField(
                  default=1000,
                  help_text="Specify the max number of seats available to the event."
                ) 

  def __unicode__(self):
    return "%s: %s" % (self.type.capitalize(), self.title)
    
  def _is_active(self):
    """Determines if the activity is available for users to participate."""
    return self.is_active_for_date(datetime.date.today())
    
  is_active = property(_is_active)
  
  def is_active_for_date(self, date):
    """Determines if the activity is available for user participation at the given date."""
    pub_result = date - self.pub_date
    expire_result = self.expire_date - date
    if pub_result.days < 0 or expire_result.days < 0:
      return False
    return True
  
  def is_event_completed(self):
    """Determines if the event is completed."""
    result = datetime.datetime.today() - self.event_date
    if result.days >= 0 and result.seconds >= 0:
      return True
    return False
    
  def _has_variable_points(self):
    """Returns true if the activity uses variable points, false otherwise."""
    if self.point_value > 0:
      return False
    else:
      return True
      
  has_variable_points = property(_has_variable_points)
  
  def liked_users(self):
    """Returns an array of users that like this activity."""
    return [like.user for like in self.likes.all()]
  
  def pick_question(self, user_id):
    """Choose a random question to present to a user."""
    if self.confirm_type != "text":
      return None
      
    questions = TextPromptQuestion.objects.filter(activity=self)
    if questions:
      return questions[user_id % len(questions)]
    else:
      return None

# These models represent the different types of activities users can commit to.
class CommonBase(models.Model):
  """Common fields to all models in this file."""
  
  created_at = models.DateTimeField(editable=False, auto_now_add=True)
  updated_at = models.DateTimeField(editable=False, auto_now=True, null=True)
    
  class Meta:
    abstract = True
    
class CommonActivityUser(CommonBase):
  """Common fields for items that need to be approved by an administrator."""
  
  STATUS_TYPES = (
    ('pending', 'Pending approval'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
  )
  
  approval_status = models.CharField(max_length=20, choices=STATUS_TYPES, default="pending")
  award_date = models.DateTimeField(null=True, blank=True, editable=False)
  submission_date = models.DateTimeField(null=True, blank=True, editable=False)

class CommitmentMemberManager(models.Manager):
  """
  Custom manager for retrieving active commitments.
  """
  def active(self):
    return self.get_query_set().filter(award_date__isnull=True)
  
  
class CommitmentMember(CommonBase):
  """Represents the join between commitments and users.  Has fields for 
  commenting on a commitment and whether or not the commitment is currently 
  active."""
  
  user = models.ForeignKey(User)
  commitment = models.ForeignKey(Commitment)
  completion_date = models.DateField()
  award_date = models.DateTimeField(blank=True, null=True)
  comment = models.TextField(blank=True)
  social_email = models.TextField(blank=True, null=True, help_text="Email address of the person the user went with.")
  social_email2 = models.TextField(blank=True, null=True, help_text="Email address of the person the user went with.")
  objects = CommitmentMemberManager()
  
  def __unicode__(self):
    return "%s : %s" % (self.commitment.title, self.user.username)
    
  def days_left(self):
    """
    Returns how many days are left before the user can submit the activity.
    """
    diff = self.completion_date - datetime.date.today()
    if diff.days < 0:
      return 0
    
    return diff.days

  def social_bonus_awarded(self):
    """
    Try to check if there is a social bonus.
    """
    if not self.commitment.is_group and self.social_email:
      try:
        ref_user = User.objects.get(email=self.social_email)
        ref_count = CommitmentMember.objects.filter(user=ref_user, commitment=self.commitment,
            award_date__isnull=False).count()
        if ref_count > 0:
          return True
      except User.DoesNotExist:
        pass

    return False

  def save(self):
    """Custom save method to set fields depending on whether or not the item is just added or if the item is completed."""
    profile = self.user.get_profile()
    
    if not self.completion_date:
      self.completion_date = datetime.date.today() + datetime.timedelta(days=self.commitment.duration)
      
    if not self.pk and profile.floor:
      # User is adding the commitment.
      message = "is participating in the commitment \"%s\"." % (
        self.commitment.title,
      )
      post = Post(user=self.user, floor=profile.floor, text=message, style_class="system_post")
      post.save()
      
    if self.award_date:
      # User has finished the commitment.
      # Award the points
      profile = self.user.get_profile()
      message = "%sCommitment: %s"  % (
          'Canopy ' if self.commitment.is_canopy else '',
          self.commitment.title
      )
      profile.add_points(self.commitment.point_value, self.award_date, message, self)
      profile.save()

      ## award social bonus to myself if the ref user had successfully completed the activity
      social_message = message + "(Social Bonus)"
      if self.social_email:
        ref_user = User.objects.get(email=self.social_email)
        ref_members = CommitmentMember.objects.filter(user=ref_user, commitment=self.commitment)
        for m in ref_members:
          if m.award_date:
            profile.add_points(self.commitment.social_bonus, self.award_date, social_message)
        
      profile.save()
      
      ## award social bonus to others who referenced my email and successfully completed the activity
      ref_members = CommitmentMember.objects.filter(commitment=self.commitment, social_email=self.user.email)
      for m in ref_members:
        if m.award_date:
          ref_profile = m.user.get_profile()
          ref_profile.add_points(self.commitment.social_bonus, self.award_date, social_message)
          ref_profile.save()
      
      if profile.floor:
        # Construct the points
        message = "has completed the commitment \"%s\"." % (
          self.commitment.title,
        )

        post = Post(user=self.user, floor=self.user.get_profile().floor, text=message, style_class="system_post")
        post.save()
        
    # Invalidate the categories cache.
    cache.delete('smartgrid-categories-%s' % self.user.username)
    cache.delete('user_events-%s' % self.user.username)
    invalidate_floor_avatar_cache(self.commitment, self.user)
    invalidate_commitments_cache(self.user)
    super(CommitmentMember, self).save()
    
    # Note, possibly_award is here because the member needs to be saved.
    badges.possibly_award_badge(user_badges.FullyCommittedBadge.slug, user=self.user)
    
  def delete(self):
    """Custom delete method to remove the points for completed commitments."""
    profile = self.user.get_profile()
    
    if self.award_date:
      title = "Commitment: %s (Removed)" % self.commitment.title
      profile.remove_points(self.commitment.point_value, self.award_date, title, self)
      profile.save()
    elif profile.floor:
      message = "is no longer participating in \"%s\"." % (
        self.commitment.title,
      )
      post = Post(user=self.user, floor=self.user.get_profile().floor, text=message, style_class="system_post")
      post.save()
      
    # Invalidate the categories cache.
    cache.delete('smartgrid-categories-%s' % self.user.username)
    cache.delete('user_events-%s' % self.user.username)
    invalidate_floor_avatar_cache(self.commitment, self.user)
    invalidate_commitments_cache(self.user)
    super(CommitmentMember, self).delete()
  

def activity_image_file_path(instance=None, filename=None, user=None):
  """Returns the file path used to save an activity confirmation image."""
  
  from components.activities import ACTIVITY_FILE_DIR
  
  if instance:
    user = user or instance.user
  return os.path.join(ACTIVITY_FILE_DIR, user.username, filename)
                    
class ActivityMember(CommonActivityUser):
  """Represents the join between users and activities."""
  
  user = models.ForeignKey(User)
  activity = models.ForeignKey(Activity)
  question = models.ForeignKey(TextPromptQuestion, null=True, blank=True)
  response = models.TextField(blank=True)
  admin_comment = models.TextField(blank=True, help_text="Reason for approval/rejection")
  social_email = models.TextField(blank=True, help_text="Email address of the person the user went with.")
  social_email2 = models.TextField(blank=True, null=True, help_text="Email address of the person the user went with.")

  image = models.ImageField(max_length=1024, 
                            blank=True, 
                            upload_to=activity_image_file_path,
                            help_text="Uploaded image for verification."
  )
  points_awarded = models.IntegerField(
      blank=True, 
      null=True, 
      help_text="Number of points to award for activities with variable point values."
  )
  notifications = generic.GenericRelation(UserNotification, editable=False)
  
  def __unicode__(self):
    return "%s : %s" % (self.activity.title, self.user.username)

  def social_bonus_awarded(self):
    """
    Try to check if there is a social bonus.
    """
    if not self.activity.is_group and self.social_email:
      try:
        ref_user = User.objects.get(email=self.social_email)
        ref_count = ActivityMember.objects.filter(user=ref_user, activity=self.activity,
            approval_status="approved").count()
        if ref_count > 0:
          return True
      except User.DoesNotExist:
        pass

    return False
        
  def save(self, *args, **kwargs):
    """Custom save method to award/remove points if the activitymember is approved or rejected."""
    if self.approval_status != "rejected":
      # Check for any notifications and mark them as read.
      self.notifications.all().update(unread=False)
      
    if self.approval_status == u"pending":
      # Mark pending items as submitted.
      self.submission_date = datetime.datetime.today()
      
    elif self.approval_status != u"approved" and self.award_date:
      # Removing user points and resetting award date.
      # Determine how many points to remove.
      if self.activity.has_variable_points:
        points = self.points_awarded
      else:
        points = self.activity.point_value
        
      profile = self.user.get_profile()
      message = "%s: %s (Rejected)" % (self.activity.type.capitalize(), self.activity.title)
      profile.remove_points(points, self.submission_date, message, self)
      profile.save()
      self.award_date = None
      # self.submission_date = None # User will have to resubmit.
      
    # Invalidate the categories cache.
    cache.delete('smartgrid-categories-%s' % self.user.username)
    cache.delete('user_events-%s' % self.user.username)
    invalidate_floor_avatar_cache(self.activity, self.user)
    super(ActivityMember, self).save()
    
    # We check here for approved and rejected items because the object needs to be saved first.
    if self.approval_status == u"approved" and not self.award_date:        
      self._handle_approved()

      super(ActivityMember, self).save()
      
    if self.approval_status == u"rejected":
      self._handle_rejected()

  def _has_noshow_penalty(self):
    # 2 days past and has submission_date (signed up)
    diff = datetime.date.today() - self.activity.event_date.date()
    if diff.days > 2 and self.submission_date:
        return True
    else:
        return False

  def _handle_approved(self):
    profile = self.user.get_profile()
    # Determine how many points to award.
    if self.activity.has_variable_points:
      points = self.points_awarded
    else:
      points = self.activity.point_value

    # Record dates.
    self.award_date = datetime.datetime.today()

    ## reverse event/excursion noshow penalty
    if (self.activity.type == "event" or self.activity.type=="excursion") and self._has_noshow_penalty():
        message = "%s: %s (Reverse No Show Penalty)" % (self.activity.type.capitalize(), self.activity.title)
        profile.add_points(4, self.submission_date, message, self)

    if not self.submission_date:
      # This may happen if it is an item with a confirmation code.
      self.submission_date = self.award_date
    
    title = "%s%s: %s" % (
        'Canopy ' if self.activity.is_canopy else '',
        self.activity.type.capitalize(), 
        self.activity.title
    )
    profile.add_points(points, self.submission_date, title, self)

    ## award social bonus to myself if the ref user had successfully completed the activity
    social_title = "%s: %s (Social Bonus)" % (self.activity.type.capitalize(), self.activity.title)
    if self.social_email:
      ref_user = User.objects.get(email=self.social_email)
      ref_members = ActivityMember.objects.filter(user=ref_user, activity=self.activity)
      for m in ref_members:
        if m.approval_status == 'approved':
          profile.add_points(self.activity.social_bonus, self.submission_date, social_title)
      
    profile.save()
    
    ## award social bonus to others referenced my email and successfully completed the activity
    ref_members = ActivityMember.objects.filter(activity=self.activity, social_email=self.user.email)
    for m in ref_members:
      if m.approval_status == 'approved':
        ref_profile = m.user.get_profile()
        ref_profile.add_points(self.activity.social_bonus, self.submission_date, social_title)
        ref_profile.save()

    ## canopy group activity need to create multiple approved members
    if self.activity.is_group:
        if self.social_email:
            group_user = User.objects.get(email=self.social_email)
            ActivityMember.objects.create(user=group_user, activity=self.activity, question=self.question,
                                                 response=self.response, admin_comment=self.admin_comment,
                                                 image=self.image, points_awarded=self.points_awarded,
                                                 approval_status=self.approval_status, award_date=self.award_date,
                                                 submission_date=self.submission_date)
        if self.social_email2:
            group_user = User.objects.get(email=self.social_email2)
            ActivityMember.objects.create(user=group_user, activity=self.activity, question=self.question,
                                                 response=self.response, admin_comment=self.admin_comment,
                                                 image=self.image, points_awarded=self.points_awarded,
                                                 approval_status=self.approval_status, award_date=self.award_date,
                                                 submission_date=self.submission_date)
    if profile.floor and not self.activity.is_canopy:
      # Post on the user's floor wall.
      message = " has been awarded %d points for completing \"%s\"." % (
        points,
        self.activity.title,
      )
      post = Post(user=self.user, floor=profile.floor, text=message, style_class="system_post")
      post.save()
    elif self.activity.is_canopy:
      from components.canopy.models import Post as CanopyPost
      
      message = " has been awarded %d karma points for completing \"%s\"." % (
        points,
        self.activity.title,
      )
      post = CanopyPost(user=self.user, text=message)
      post.save()
       
  def _handle_rejected(self):
    """
    Creates a notification for rejected tasks.  This also creates an email message if it is configured.
    """
    # Construct the message to be sent.
    message = "Your response to <a href='%s'>%s</a> %s was not approved." % (
        reverse("activity_task", args=(self.activity.type, self.activity.slug,)),
        self.activity.title, 
        # The below is to tell the javascript to convert into a pretty date.
        # See the prettyDate function in media/js/makahiki.js
        "<span class='rejection-date' title='%s'></span>" % self.submission_date.isoformat(),
    )
    
    message += " You can still get points by clicking on the link and trying again."
    
    UserNotification.create_error_notification(self.user, message, content_object=self)
    
    subject = "[%s] Your response to '%s' was not approved" % (settings.COMPETITION_NAME, self.activity.title) 
    current_site = Site.objects.get(id=settings.SITE_ID)
    message = render_to_string("email/rejected_activity.txt", {
      "object": self,
      "COMPETITION_NAME": settings.COMPETITION_NAME,
      "domain": current_site.domain,
    })
    html_message = render_to_string("email/rejected_activity.html", {
      "object": self,
      "COMPETITION_NAME": settings.COMPETITION_NAME,
      "domain": current_site.domain,
    })
    
    UserNotification.create_email_notification(self.user.email, subject, message, html_message)
    
  def delete(self):
    """Custom delete method to remove awarded points."""
    
    if self.approval_status == u"approved":
      # Determine how many points to award.
      if self.activity.has_variable_points:
        points = self.points_awarded
      else:
        points = self.activity.point_value
        
      profile = self.user.get_profile()
      message = "%s: %s (Removed)" % (self.activity.type.capitalize(), self.activity.title)
      profile.remove_points(points, self.submission_date, message, self)
      profile.save()
      
    # Invalidate the categories cache.
    cache.delete('smartgrid-categories-%s' % self.user.username)
    cache.delete('user_events-%s' % self.user.username)
    invalidate_floor_avatar_cache(self.activity, self.user)
    super(ActivityMember, self).delete()

#------ Reminders --------#
from django.contrib.localflavor.us.models import PhoneNumberField
from components.makahiki_profiles.models import Profile

REMINDER_CHOICES = (
    ("email", "Email"),
    ("text", "Text"),
)

class Reminder(models.Model):
  """
  Sends a reminder for an activity to a user.  Reminders are queued up and sent later.
  """
  user = models.ForeignKey(User, editable=False)
  activity = models.ForeignKey(ActivityBase, editable=False)
  send_at = models.DateTimeField()
  sent = models.BooleanField(default=False, editable=False)
  created_at = models.DateTimeField(editable=False, auto_now_add=True)
  updated_at = models.DateTimeField(editable=False, auto_now=True, null=True)
  
  class Meta:
    abstract = True
    unique_together = ("user", "activity")
    
  def send(self):
    raise NotImplementedError("Reminder subclasses need to implement send.")
    
class EmailReminder(Reminder):
  email_address = models.EmailField()
  
  def send(self):
    """
    Sends a reminder email to the user.
    """
    if not self.sent:
      subject = "[%s] Reminder for %s" % (settings.COMPETITION_NAME, self.activity.title) 
      current_site = Site.objects.get(id=settings.SITE_ID)
      message = render_to_string("email/activity_reminder.txt", {
        "activity": self.activity,
        "user": self.user,
        "COMPETITION_NAME": settings.COMPETITION_NAME,
        "domain": current_site.domain,
      })
      html_message = render_to_string("email/activity_reminder.html", {
        "activity": self.activity,
        "user": self.user,
        "COMPETITION_NAME": settings.COMPETITION_NAME,
        "domain": current_site.domain,
      })

      UserNotification.create_email_notification(self.email_address, subject, message, html_message)
      self.sent = True
      self.save()
    
class TextReminder(Reminder):
  TEXT_CARRIERS = (
    ('att', 'AT&T'),
    ('sprint', 'Sprint'),
    ('tmobile', 'T-Mobile'),
    ('verizon', 'Verizon'),
    ('mobi', 'Mobi PCS'),
    ('virgin', 'Virgin Mobile'),
    ('alltel', "AllTel"),
  )
  TEXT_EMAILS = {
      "att": "txt.att.net",
      "verizon": "vtext.com",
      "tmobile": "tmomail.net",
      "sprint": "messaging.sprintpcs.com",
      "mobi": "mobipcs.net",
      "virgin": "vmobl.com",
      "alltel": "message.alltel.com",
  }
  text_number = PhoneNumberField()
  text_carrier = models.CharField(max_length=50, choices=TEXT_CARRIERS, null=True, blank=True)
  
  def send(self):
    """
    Sends a reminder text to the user via an email.
    """
    number = self.text_number.replace("-", "")
    email = number + "@" + self.TEXT_EMAILS[self.text_carrier]
    if not self.sent:
      # subject = "[%s] Reminder for %s" % (settings.COMPETITION_NAME, self.activity.title) 
      current_site = Site.objects.get(id=settings.SITE_ID)
      message = render_to_string("email/activity_text_reminder.txt", {
        "activity": self.activity,
        "user": self.user,
      })

      UserNotification.create_email_notification(email, "", message)
      self.sent = True
      self.save()
      