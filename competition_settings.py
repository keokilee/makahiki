# competition_settings.py
# This file contains settings for the current competition.
# This include start and end dates along with round information.

# The start and end date of the competition.
COMPETITION_START = '2011-01-01'
COMPETITION_END = '2011-12-31'

# The rounds of the competition. Specify dates using "yyyy-mm-dd".
# Start means the competition will start at midnight on that date.
# End means the competition will end at midnight of that date.
# This means that a round that ends on "2010-08-02" will end at 11:59pm of August 2nd.
COMPETITION_ROUNDS = {
  "Round 1" : {
    "start": '2011-04-08',
    "end": '2011-12-31',
  },
}
