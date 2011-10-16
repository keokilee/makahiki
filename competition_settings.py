# competition_settings.py
# This file contains settings for the current competition.
# This include start and end dates along with round information.
import datetime # Only used to dynamically set the round dates.

# The start and end date of the competition.
COMPETITION_START = "2011-10-14"
COMPETITION_END = "2011-10-17"

# The rounds of the competition. Specify dates using "yyyy-mm-dd".
# Start means the competition will start at midnight on that date.
# End means the competition will end at midnight of that date.
# This means that a round that ends on "2010-08-02" will end at 11:59pm of August 2nd.
COMPETITION_ROUNDS = {
  "Round 1" : {
    "start": "2011-10-14",
    "end": "2011-10-15",
  },
  'Round 2': {
    'start': '2011-10-15',
    'end': '2011-10-16',
  }
}

# When enabled, users who try to access the site before or after the competition ends are blocked.
# Admin users are able to log in at any time.
CAN_ACCESS_OUTSIDE_COMPETITION = False
