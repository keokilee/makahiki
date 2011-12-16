from django.core import management
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.sites.models import Site
from django.template.loader import render_to_string

from components.makahiki_profiles.models import Profile
from components.makahiki_notifications.models import UserNotification, NoticeTemplate

class Command(management.base.BaseCommand):
  help = 'Adds the top n users in points to the canopy.'
  
  def handle(self, *args, **options):
    """
    Adds the top n users to the canopy.
    """
    if len(args) != 1:
      self.stdout.write("Usage: python manage.py add_canopy_members <num_users>\n")
      return
      
    count = 0
    try:
      count = int(args[0])
    except ValueError:
      self.stdout.write("Num users must be an integer value\n")
      return
      
    if count <= 0:
      self.stdout.write("Num users must be greater than 0\n")
      return
      
    eligible_members = Profile.objects.order_by("-points")[:count]
    self.stdout.write("%d members are eligible for the canopy.\n" % count)
    for member in eligible_members:
      if member.canopy_member:
        self.stdout.write("'%s' is already a member.  Skipping\n" % member.name)
      else:
        self.__create_notifications(member.user)
        member.canopy_member = True
        member.save()
        
  def __create_notifications(self, user):
    try:
      template = NoticeTemplate.objects.get(notice_type='canopy-elevation')
      contents = template.render()
      UserNotification.create_info_notification(user, contents, True)
      
    except NoticeTemplate.DoesNotExist:
      # Use default message.
      message = "Congratulations! You have been added to the canopy!" 
      UserNotification.create_info_notification(user, message, True)

    if user.email and len(user.email) > 0:
      subject = "[%s] Congratulations! You have been added to the canopy!" % (settings.COMPETITION_NAME,) 
      current_site = Site.objects.get(id=settings.SITE_ID)
      message = render_to_string("email/added_to_canopy.txt", {
          "user": user,
          "competition_name": settings.COMPETITION_NAME,
          "domain": current_site.domain,
      })
      html_message = render_to_string("email/added_to_canopy.html", {
          "user": user,
          "competition_name": settings.COMPETITION_NAME,
          "domain": current_site.domain,
      })
      self.stdout.write('Sending email to %s\n' % user.email)
      UserNotification.create_email_notification(user.email, subject, message, html_message)
      
    else:
      self.stdout.write("'%s' does not have a valid email address.  Skipping\n" % user.username)