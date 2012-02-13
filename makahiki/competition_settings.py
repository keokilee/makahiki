# competition_settings.py
# This file contains settings for the current competition.
# This include start and end dates along with round information.
import datetime # Only used to dynamically set the round dates.

# The start and end date of the competition.
COMPETITION_START = (datetime.date.today() - datetime.timedelta(days=3)).strftime("%Y-%m-%d")
COMPETITION_END = (datetime.date.today() + datetime.timedelta(days=6)).strftime("%Y-%m-%d")

# The rounds of the competition. Specify dates using "yyyy-mm-dd".
# Start means the competition will start at midnight on that date.
# End means the competition will end at midnight of that date.
# This means that a round that ends on "2010-08-02" will end at 11:59pm of August 1st.
COMPETITION_ROUNDS = {
  "Round 1" : {
    "start": (datetime.date.today() - datetime.timedelta(days=3)).strftime("%Y-%m-%d"),
    "end": (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
  },
}

# When enabled, users who try to access the site before or after the competition ends are blocked.
# Admin users are able to log in at any time.
CAN_ACCESS_OUTSIDE_COMPETITION = True