import sys
from datetime import datetime, timedelta

from django.core import management
from django.contrib.auth.models import User

from components.makahiki_profiles.models import PointsTransaction

# Start and end dates that we are looking at.
START_DATE = datetime(2011, 10, 18) # Note we look at the day after the start.
END_DATE = datetime(2011, 11, 7)

class Command(management.base.BaseCommand):
    help = "Analyses the scores of the users over a period of time."
    args = "<output filename>"

    def handle(self, *args, **options):
        if len(args) != 1:
            print "A file name is required."
            return
        outfile = open(args[0], 'w')
        if not outfile:
            print "Could not open file '%s'" % args[0]
            
        # Construct the header of the file.
        dates = []
        days = (END_DATE - START_DATE).days
        for day in range(0, days + 1): # range is not inclusive
            date = (START_DATE + timedelta(days=day)).strftime('%Y-%m-%d')
            dates.append(date)

        outfile.write('user,' + ','.join(dates) + '\n')

        users = User.objects.filter(
              profile__points__gt=0,
        ).order_by('id')
        
        count = users.count()
        for index, user in enumerate(users):
            print "Processing %s (%d/%d)" % (user.username, index + 1, count)
            # Get the points on each date for the user.
            totals = [str(self._get_points_on_date(user, date)) for date in dates]
            outfile.write(("%d," % user.id) + ",".join(totals) + "\n")
            
        outfile.close()
        
    def _get_points_on_date(self, user, date):
        logs = PointsTransaction.objects.filter(
                user=user, 
                submission_date__lte=date, 
        ).exclude(message__startswith="Canopy Activity")
        return sum([log.points for log in logs])
