# default.py
#
# This file maps ids to a string of classes.  Templates that use class_tags and insert_classes refer to this file.
# Note that some of the "ids" are more like class names.  These rules act like "macro expansions" in the templates.

# If True, the classes will be inserted.  Otherwise, the tags will be empty strings.
RETURN_CLASSES = True

CSS_IMPORTS = """
<link rel="stylesheet" href="{0}css/{1}/screen.css" media="screen">
<link rel="stylesheet" href="{0}css/{1}/print.css" media="print">
<link rel="stylesheet" href="{0}css/{1}/jquery-ui.css">
<!--[if lt IE 8]><link rel="stylesheet" href="{0}css/{1}/ie.css" 
type="text/css" media="screen, projection"><![endif]-->

<link rel="stylesheet" href="{0}frontendadmin/css/frontendadmin.css" />
<link rel="stylesheet" href="{0}uni_form/uni-form.css" />
"""

JS_IMPORTS = """
<script src="{0}js/jquery-1.4.2.min.js" type="text/javascript"></script>
<script src="{0}js/jquery-ui-1.8.1.custom.min.js" type="text/javascript"></script>
<script src="{0}js/jquery.cycle.lite.1.0.min.js" type="text/javascript"></script>
<script src="{0}js/jquery.form.2.43.js" type="text/javascript"></script>
"""

LOGGED_IN_CSS_IMPORT = '<link rel="stylesheet" href="{0}css/{1}/logged_in_base.css">'

PAGE_CSS_IMPORT = {
  "home": '<link rel="stylesheet" href="{0}css/{1}/pages/home.css">',
  "landing": '<link rel="stylesheet" href="{0}css/{1}/pages/landing.css">',
  "mobile": '<link rel="stylesheet" href="{0}css/{1}/pages/mobile.css">',
  "news": '<link rel="stylesheet" href="{0}css/{1}/pages/news.css">\n<script src="{0}js/news.js" type="text/javascript"></script>',
  "view_activities": '<link rel="stylesheet" href="{0}css/{1}/pages/view_activities.css">',
  "view_energy": '<link rel="stylesheet" href="{0}css/{1}/pages/view_energy.css">',
  "view_help": '<link rel="stylesheet" href="{0}css/{1}/pages/view_help.css">',
  "view_prizes": '<link rel="stylesheet" href="{0}css/{1}/pages/view_prizes.css">',
  "view_profile": '<link rel="stylesheet" href="{0}css/{1}/pages/view_profile.css">',
}
CSS_IDS = {
  "header": "span-24 last",
  "header-logo": "span-2",
  "header-title": "span-3",
  "header-info": "span-12",
  "header-nav": "span-7 last",
  "header-user-info": "span-4",
  "header-avatar": "span-2",
  "header-user-username": "span-4 last",
  "header-user-points": "span-2",
  "header-user-rank": "span-2 last",
  "header-floor-info": "span-4 last",
  "header-floor-name": "span-4 last",
  "header-floor-points": "span-2",
  "header-floor-energy": "span-2",
  "header-floor-rank": "span-2 last",
  "header-floor-image": "span-2 last",
  "header-nav-links": "span-7 last",
  "header-logout": "span-7 last",

  "notification": "span-24 last",
  "notification_box": "ui-accordion-content ui-widget-content ui-corner-all ui-accordion-content-active",
  
  "user-cycle": "span-4 last",
  "floor-cycle": "span-4 last",
  
  "home-energy": "span-11",
  "home-activities": "span-11 prepend-1 last",
  "home-news": "span-6 prepend-2",
  "home-prizes": "span-6 prepend-7 last",
  "home-help": "span-6 prepend-5",
  "home-profile": "span-6 prepend-1 last",
  
  "news-events-popular-activities": "span-8",
  "news-wall": "span-15 prepend-1 last",
  "news-events": "widget ui-corner-all ui-accordion ui-widget ui-accordion-icons",
  "news-events-title": "widget-title ui-state-active ui-accordion-header ui-corner-top",
  "news-events-content": "widget-body ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom ui-accordion-content-active",
  "news-most-popular-title": "widget-title ui-state-active ui-accordion-header ui-corner-top",
  "news-most-popular-content": "widget-body ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom ui-accordion-content-active",
  "news-commitments-title": "widget-title ui-state-active ui-accordion-header ui-corner-top",
  "news-commitments-content": "widget-body ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom ui-accordion-content-active",
  "news-commitments": "widget ui-corner-all ui-accordion ui-widget ui-accordion-icons",
  "news-most-popular": "widget ui-corner-all ui-accordion ui-widget ui-accordion-icons",
  "news-wall-box": "widget ui-corner-all ui-accordion ui-widget ui-accordion-icons",
  "news-wall-title": "widget-title ui-state-active ui-accordion-header ui-corner-top",
  "news-wall-content": "widget-body ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom ui-accordion-content-active",
  "news-commitments-title": "widget-title ui-state-active ui-accordion-header ui-corner-top",
  "wall-form": "padding: 0; padding-bottom: 5px; border-bottom: 1px solid #DFD9C3",
  "wall-post": "",
  
  "profile-form": "span-8",
  "profile-form-box": "widget ui-corner-all ui-accordion ui-widget ui-accordion-icons",
  "profile-form-title": "widget-title ui-state-active ui-accordion-header ui-corner-top",
  "profile-form-content": "widget-body ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom ui-accordion-content-active",
  "profile-badges": "span-8",
  "profile-badges-box": "widget ui-corner-all ui-accordion ui-widget ui-accordion-icons",
  "profile-badges-title": "widget-title ui-state-active ui-accordion-header ui-corner-top",
  "profile-badges-content": "widget-body ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom ui-accordion-content-active",
  "profile-history": "span-8 last",
  "profile-history-box": "widget ui-corner-all ui-accordion ui-widget ui-accordion-icons",
  "profile-history-title": "widget-title ui-state-active ui-accordion-header ui-corner-top",
  "profile-history-content": "widget-body ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom ui-accordion-content-active",
  "profile-form-submit-button": "ui-button ui-state-default ui-corner-all",
  
  "landing-logo": "span-3",
  "landing-title": "span-21 last",
  "landing-intro": "span-12",
  "landing-poster": "span-12 last",
  "landing-page": "span-24 last",
  "landing-poster": "",
  "landing-sponsors": "span-24 last",
  "landing-button-participant": "ui-button ui-widget ui-corner-all ui-state-active",
  "landing-button-non-participant": "ui-button ui-widget ui-corner-all ui-state-active",
  
  "energy-power-scoreboard": "span-6",
  "energy-status": "span-18 last",
  "energy-power": "widget ui-corner-all ui-accordion ui-widget ui-accordion-icons",
  "energy-power-title": "widget-title ui-state-active ui-accordion-header ui-corner-top",
  "energy-power-content": "widget-body ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom ui-accordion-content-active",
  "energy-scoreboard": "widget ui-corner-all ui-accordion ui-widget ui-accordion-icons",
  "energy-scoreboard-title": "widget-title ui-state-active ui-accordion-header ui-corner-top",
  "energy-scoreboard-content": "widget-body ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom ui-accordion-content-active",
  "energy-status-box": "widget ui-corner-all ui-accordion ui-widget ui-accordion-icons",
  "energy-status-title": "widget-title ui-state-active ui-accordion-header ui-corner-top",
  "energy-status-content": "widget-body ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom ui-accordion-content-active",

  "activity-events-scoreboard": "span-8",
  "activity-events-box": "widget ui-corner-all ui-accordion ui-widget ui-accordion-icons",
  "activity-events-title": "widget-title ui-state-active ui-accordion-header ui-corner-top",
  "activity-events-content": "widget-body ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom ui-accordion-content-active",
  "activity-scoreboard-box": "widget ui-corner-all ui-accordion ui-widget ui-accordion-icons",
  "activity-scoreboard-title": "widget-title ui-state-active ui-accordion-header ui-corner-top",
  "activity-scoreboard-content": "widget-body ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom ui-accordion-content-active",
  "activity-grid": "span-16 last",
  "activity-grid-box": "",
  "activity-grid-title": "widget-title ui-state-active ui-accordion-header ui-corner-top",
  "activity-grid-content": "widget-body ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom ui-accordion-content-active",

  "activity-category": "ui-accordion-content ui-widget-content ui-corner-all ui-accordion-content-active",  
  "activity-category-tasks": "span-24 last",
  "activity-category-task": "ui-accordion-content ui-widget-content ui-corner-all ui-accordion-content-active",
  "activity-task-stats":"span-9",
  "activity-task-details":"span-15 last",
  
  "prizes-list": "span-11",
  "prizes-list-box": "widget ui-corner-all ui-accordion ui-widget ui-accordion-icons",
  "prizes-list-title": "widget-title ui-state-active ui-accordion-header ui-corner-top",
  "prizes-list-content": "widget-body ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom ui-accordion-content-active",
  "prizes-raffle-box": "widget ui-corner-all ui-accordion ui-widget ui-accordion-icons",
  "prizes-raffle-title": "widget-title ui-state-active ui-accordion-header ui-corner-top",
  "prizes-raffle-content": "widget-body ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom ui-accordion-content-active",
  "prizes-raffle": "span-13 last",
  "prizes-raffle-info": "span-10 last",
  
  "help-video": "span-8",
  "help-video-box": "widget ui-corner-all ui-accordion ui-widget ui-accordion-icons",
  "help-video-title": "widget-title ui-state-active ui-accordion-header ui-corner-top",
  "help-video-content": "widget-body ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom ui-accordion-content-active",
  "help-rules-box": "widget ui-corner-all ui-accordion ui-widget ui-accordion-icons",
  "help-rules-title": "widget-title ui-state-active ui-accordion-header ui-corner-top",
  "help-rules-content": "widget-body ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom ui-accordion-content-active",
  "help-faq-box": "widget ui-corner-all ui-accordion ui-widget ui-accordion-icons",
  "help-faq-title": "widget-title ui-state-active ui-accordion-header ui-corner-top",
  "help-faq-content": "widget-body ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom ui-accordion-content-active",
  "help-ask-box": "widget ui-corner-all ui-accordion ui-widget ui-accordion-icons",
  "help-ask-title": "widget-title ui-state-active ui-accordion-header ui-corner-top",
  "help-ask-content": "widget-body ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom ui-accordion-content-active",
  "help-rules": "span-7 prepend-1",
  "help-faq": "span-7 prepend-1 last",
  "help-ask": "span-15 prepend-9 last",
  "help-ask-form": "span-14 last",
  "help-ask-submit": "span-14 last",
}

CSS_CLASSES = {
  "prizes-add-button": "ui-button ui-state-default ui-corner-all",
  "prizes-remove-button": "ui-button ui-state-error ui-corner-all",
  "prizes-disabled-button": "ui-button ui-state-disabled ui-corner-all",
  
  "widget": "widget ui-corner-all ui-accordion ui-widget ui-accordion-icons",
  "widget-title": "widget-title ui-state-active ui-accordion-header ui-corner-top",
  "widget-body": "widget-body ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom ui-accordion-content-active",
  "ui-button": "ui-button ui-state-default ui-corner-all",
  
  "activity-task-button": "ui-button ui-state-default ui-corner-all",
  
  "user-post": "span-14 last",
  'user-post-avatar': "span-2",
  'news-photo': "photo",
  'user-post-content': "span-12 last",
  'user-post-date-string': "date_string",
}
