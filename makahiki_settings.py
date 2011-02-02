# makahiki_settings.py
# This file contains organizational-level settings for the competition.
# These settings include the name of the competition and theme settings.

# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
# Overrides time zone specified in settings.py
TIME_ZONE = 'Pacific/Honolulu'

# Settings for the CAS authentication service.
CAS_SERVER_URL = 'https://login.its.hawaii.edu/cas/'
CAS_REDIRECT_URL = '/home'
CAS_IGNORE_REFERER = True

# The actual name of the competition.
COMPETITION_NAME = "Kukui Cup"

# Optional setting to specify a special name for the points. Default is "points".
COMPETITION_POINT_NAME = "Kukui Nut"

# The name of a standard competition grouping.  Defaults to "Floor" if this is not provided.
COMPETITION_GROUP_NAME = "Lounge"

# Enable the CSS theme selector at the top of the page.
ENABLE_CSS_SELECTOR = False

# The theme to use as default. This corresponds to a folder in media that contains the CSS.
MAKAHIKI_THEME = "default"

# Kukui Cup Template theme setting.
MAKAHIKI_TEMPLATE_THEME = 'default'

# Theme settings for Makahiki.  Used to aid in styling the Javascript widgets.
# The system will insert the colors based on the selected theme.  If an entry 
# for a theme does not exist, default will be used.
MAKAHIKI_THEME_SETTINGS = {
  "default" : {
    "widgetBackgroundColor" : 'F5F3E5',
    "widgetHeaderColor" : '459E00',
    "widgetHeaderTextColor" : 'white',
    "widgetTextColor" : '312E25',
    "widgetTextFont" : 'Ariel, sans serif',
    "windowNavBarColor" : '2F6B00',
  },
  "cupertino" : {
    "widgetBackgroundColor" : 'F2F5F7',
    "widgetHeaderColor" : '459E00',
    "widgetHeaderTextColor" : 'white',
    "widgetTextColor" : '312E25',
    "widgetTextFont" : 'Ariel, sans serif',
    "windowNavBarColor" : '2F6B00',
  },
  "start" : {
    "widgetBackgroundColor" : 'fff',
    "widgetHeaderColor" : '459E00',
    "widgetHeaderTextColor" : 'white',
    "widgetTextColor" : '312E25',
    "widgetTextFont" : 'Ariel, sans serif',
    "windowNavBarColor" : '2F6B00',
  },
}