import datetime

DEMO_START_DELTA = datetime.timedelta(days=1)
DEMO_END_DELTA = datetime.timedelta(days=13)

# The base date of the competition according to the fixtures.
FIXTURE_BASE_DATE = "2011-01-27"

# The start and end date of the competition.
COMPETITION_START = (datetime.date.today() - DEMO_START_DELTA).strftime("%Y-%m-%d")
COMPETITION_END = (datetime.date.today() + DEMO_END_DELTA).strftime("%Y-%m-%d")

# The rounds of the competition. Specify dates using "yyyy-mm-dd".
# Start means the competition will start at midnight on that date.
# End means the competition will end at midnight of that date.
# This means that a round that ends on "2010-08-02" will end at 11:59pm of August 2nd.
COMPETITION_ROUNDS = {
  "Round 1" : {
    "start": COMPETITION_START,
    "end": (datetime.date.today() - DEMO_START_DELTA + datetime.timedelta(days=6)).strftime("%Y-%m-%d"),
  },
}
