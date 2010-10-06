import datetime
import random

from django.core import management
from django.conf import settings

from makahiki_profiles.models import Profile, ScoreboardEntry
from activities.models import Activity, Commitment, ActivityMember, CommitmentMember
from activities import get_current_commitments

class Command(management.base.BaseCommand):
  help = 'Simulates activity in the competition.'
  
  def handle(self, *args, **options):
    self.stdout.write("Using %s database '%s'\n" % 
          (settings.DATABASES["default"]["ENGINE"], settings.DATABASES["default"]["NAME"]))
    
    self.stdout.write("\nWARNING: The following command will result in the IRREVERSIBLE loss of data in the current database.\n")
    value = raw_input("Do you wish to continue (Y/n)? ")
    while value != "Y" and value != "n":
      self.stdout.write("Invalid option %s\n" % value)
      value = raw_input("Do you want to continue (y/n)? ")
    if value == "n":
      self.stdout.write("Operation cancelled.\n")
      return
      
    self.refresh_users()
    self.refresh_activities()
    self.adjust_activity_dates()
    self.simulate_activities_for_round_1()
    self.simulate_commitments()
      
  def refresh_users(self):
    self.stdout.write("Clearing profiles, scoreboard entries, and floors.\n")
    management.call_command('reset', 'makahiki_profiles', 'floors', interactive=False)
    self.stdout.write("Reloading users, profiles, and floors.\n")
    management.call_command('loaddata', 'fixtures/demo_users.json', verbosity=0)
    for entry in ScoreboardEntry.objects.all():
      entry.delete()
      
  def refresh_activities(self):
    self.stdout.write("Clearing activities and commitments.\n")
    management.call_command('reset', 'activities', interactive=False)
    self.stdout.write("Reloading activities and commitments.\n")
    management.call_command('loaddata', 'fixtures/demo_tasks.json', verbosity=0)
      
  def adjust_activity_dates(self):
    self.stdout.write("Adjusting activity publication, expiration, and event dates.\n")
    base_date = datetime.datetime.strptime(settings.FIXTURE_BASE_DATE, "%Y-%m-%d").date()
    start_date = datetime.datetime.strptime(settings.COMPETITION_START, "%Y-%m-%d").date()
    # Adjust activity publication dates based on the start date of the demo data.
    for activity in Activity.objects.all():
      delta = activity.pub_date - base_date
      activity.pub_date = start_date + delta
      delta = activity.expire_date - base_date
      activity.expire_date = start_date + delta
      if activity.is_event:
        delta = activity.event_date - datetime.datetime.combine(base_date, datetime.time())
        activity.event_date = start_date + delta
        activity.event_date = datetime.datetime.combine(activity.event_date, datetime.time(hour=19))
      
      activity.save()
      
  def simulate_activities_for_round_1(self):
    round_start = datetime.datetime.strptime(settings.COMPETITION_ROUNDS["Round 1"]["start"], "%Y-%m-%d").date()
    round_end = datetime.datetime.strptime(settings.COMPETITION_ROUNDS["Round 1"]["end"], "%Y-%m-%d").date()
    date_delta = (round_end - round_start).days
    self.stdout.write("Simulating activity participation in the first round.\n")
    
    activities = Activity.objects.filter(pub_date__gte=round_start, expire_date__lt=round_end)
    for profile in Profile.objects.exclude(user__username="admin"):
      # Assume user will participate between 0 and 3 activities
      # Random activity from http://stackoverflow.com/questions/962619/how-to-pull-a-random-record-using-djangos-orm
      user_activities = activities.order_by("?")[0:random.randint(0, 3)]
      for activity in user_activities:
        member = ActivityMember(user=profile.user, activity=activity)
        member.submission_date = datetime.datetime.combine(round_start, datetime.time()) + datetime.timedelta(days=random.randint(0, date_delta))
        member.approval_status = "approved"
        member.save()
        
  def simulate_commitments(self):
    competition_start = datetime.datetime.strptime(settings.COMPETITION_START, "%Y-%m-%d").date()
    today = datetime.date.today()
    date_delta = (today - competition_start).days
    self.stdout.write("Simulating commitment participation.\n")
    
    commitments = Commitment.objects.all()
    for profile in Profile.objects.exclude(user__username="admin"):
      # Assume users will participate in between 0 and 7 commitments.
      for i in range(0, random.randint(0, 7)):
        commitment = None
        while(True):
          commitment = commitments.order_by("?")[0]
          # Check if user is already participating in this commitment.
          if commitment not in get_current_commitments(profile.user):
            break
        
        member = CommitmentMember(user=profile.user, commitment=commitment)
        member.completion_date = competition_start + datetime.timedelta(days=random.randint(5, date_delta + 5))
        if member.completion_date < today:
          member.award_date = datetime.datetime.combine(member.completion_date, datetime.time())
          
        member.save()
        
  def simulate_activities_for_round_2(self):
    round_start = datetime.datetime.strptime(settings.COMPETITION_ROUNDS["Round 2"]["start"], "%Y-%m-%d").date()
    round_end = datetime.datetime.strptime(settings.COMPETITION_ROUNDS["Round 2"]["end"], "%Y-%m-%d").date()
    date_delta = (round_end - round_start).days
    self.stdout.write("Simulating activity participation in the second round.\n")
    
    for profile in Profile.objects.all():
      pass