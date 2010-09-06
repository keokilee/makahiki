# The name of a standard competition grouping.  Defaults to "Floor" if this is not provided.
COMPETITION_GROUP_NAME = "Lounge"

# The start and end date of the competition.
COMPETITION_START = '2010-07-28'
COMPETITION_END = '2010-12-31'

# The rounds of the competition. Specify dates using "yyyy-mm-dd".
# Start means the competition will start at midnight on that date.
# End means the competition will end at midnight of that date.
# This means that a round that ends on "2010-08-02" will end at 11:59pm of August 2nd.
COMPETITION_ROUNDS = {
  "Round 1" : {
    "start": '2010-08-09',
    "end": '2010-12-31',
  },
}

# The theme to use as default. This corresponds to a folder in media that contains the CSS.
MAKAHIKI_THEME = "default"

# Theme settings for Makahiki.  Used to aid in styling the Javascript widgets.
# The system will insert the colors based on the selected theme.  If an entry 
# for a theme does not exist, default will be used.
MAKAHIKI_THEME_SETTINGS = {
  "default" : {
    "widgetBackgroundColor" : '#F5F3E5',
    "widgetHeaderColor" : '#459E00',
    "widgetHeaderTextColor" : 'white',
    "widgetTextColor" : '#312E25',
    "widgetTextFont" : 'Ariel, sans serif',
    "windowNavBarColor" : '#2F6B00',
  },
}