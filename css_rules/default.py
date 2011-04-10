# default.py
#
# This file maps ids to a string of classes.  Templates that use class_tags and insert_classes refer to this file.
# Note that some of the "ids" are more like class names.  These rules act like "macro expansions" in the templates.

# If True, the classes will be inserted.  Otherwise, the tags will be empty strings.
RETURN_CLASSES = True

CSS_IMPORTS = """
<link rel="stylesheet" href="{0}css/{1}/jquery-ui.css">
<link rel="stylesheet" href="{0}css/{1}/screen.css">

<link rel="stylesheet" href="{0}frontendadmin/css/frontendadmin.css" />
<link rel="stylesheet" href="{0}uni_form/uni-form.css" />
"""

JS_IMPORTS = """
<script src="{0}js/jquery-1.4.2.min.js" type="text/javascript"></script>
<script src="{0}js/jquery-ui-1.8.1.custom.min.js" type="text/javascript"></script>
<script src="{0}js/jquery.cycle.lite.1.0.min.js" type="text/javascript"></script>
<script src="{0}js/jquery.form.2.43.js" type="text/javascript"></script>

<script type="text/javascript" src="http://www.google.com/jsapi"></script>
<script type="text/javascript" src="http://wattdepot-gdata.googlecode.com/svn/trunk/src/javascript/ajile/com.iskitz.ajile.js?mvcoff,mvcshareoff,refresh"></script>
<script type="text/javascript" src="http://wattdepot-gdata.googlecode.com/svn/trunk/src/javascript/gdataloader/org.wattdepot.gdata.GDataLoader.js"></script>
<script type="text/javascript" src="http://wattdepot-gdata.googlecode.com/svn/trunk/src/javascript/energyrank/org.wattdepot.gdata.makahiki.EnergyRank.js"></script>
"""

LOGGED_IN_CSS_IMPORT = '<link rel="stylesheet" href="{0}css/{1}/logged_in_base.css">'

PAGE_CSS_IMPORT = {
  "home": '<link rel="stylesheet" href="{0}css/{1}/pages/home.css">',
  "landing": '<link rel="stylesheet" href="{0}css/{1}/pages/landing.css">',
  "mobile": '<link rel="stylesheet" href="{0}css/{1}/pages/mobile.css">',
  "news": '<link rel="stylesheet" href="{0}css/{1}/pages/news.css">\n<script src="{0}js/news.js" type="text/javascript"></script>',
  "view_activities": '<link rel="stylesheet" href="{0}css/{1}/pages/view_activities.css">',
  "view_energy": '<link rel="stylesheet" href="{0}css/{1}/pages/view_energy.css">\n<script src="{0}js/news.js" type="text/javascript"></script>',
  "view_help": '<link rel="stylesheet" href="{0}css/{1}/pages/view_help.css">',
  "view_prizes": '<link rel="stylesheet" href="{0}css/{1}/pages/view_prizes.css">',
  "view_profile": '<link rel="stylesheet" href="{0}css/{1}/pages/view_profile.css">',
}
CSS_IDS = {
  "landing-sponsors": "content-box",
  "landing-sponsors-title": "content-box-title",
  
  "home-energy": "home-item",
  "home-activities": "home-item",
  "home-news": "home-item",
  "home-prizes": "home-item",
  "home-help": "home-item",
  "home-profile": "home-item",
  
  "energy-power": "content-box",
  "energy-scoreboard": "content-box",
  "energy-status-box": "content-box",
  "energy-power-title": "content-box-title",
  "energy-scoreboard-title": "content-box-title",
  "energy-status-title": "content-box-title",
  
  "activity-events-box": "content-box",
  "activity-scoreboard-box": "content-box",
  "activity-categories": "content-box",
  "activity-task-stats-box": "content-box",
  "activity-task-details-box": "content-box",
  "activity-events-title": "content-box-title",
  "activity-scoreboard-title": "content-box-title",
  "activity-task-stats-title": "content-box-title",
  "activity-task-details-title": "content-box-title",
  
  "news-wall": "content-box",
  "news-events": "content-box",
  "news-commitments": "content-box",
  "news-most-popular": "content-box",
  "news-wall-title": "content-box-title",
  "news-events-title": "content-box-title",
  "news-commitments-title": "content-box-title",
  "news-most-popular-title": "content-box-title",
  
  "help-video": "content-box",
  "help-rules": "content-box",
  "help-faq": "content-box",
  "help-ask": "content-box",
  "help-request": "content-box",
  "help-video-title": "content-box-title",
  "help-rules-title": "content-box-title",
  "help-faq-title": "content-box-title",
  "help-ask-title": "content-box-title",
  "help-request-title": "content-box-title",
  "help-video-content": "content-box-contents",
  "help-rules-content": "content-box-contents",
  "help-faq-content": "content-box-contents",
  "help-reqeuest-content": "content-box-contents",
  
  "profile-form-box": "content-box",
  "profile-badges-box": "content-box",
  "profile-history-box": "content-box",
  "profile-form-title": "content-box-title",
  "profile-badges-title": "content-box-title",
  "profile-history-title": "content-box-title",
  "profile-form-fb-header": "profile-section-header",
  "profile-form-general-header": "profile-section-header",
  "profile-form-contact-header": "profile-section-header",
  "profile-form-display-name-label": "profile-form-label",
  "profile-form-picture-label": "profile-form-label",
  "profile-form-about-label": "profile-form-label",
  "profile-form-logged-in-label": "profile-form-label",
  "profile-form-fb-profile-label": "profile-form-label",
  "profile-form-contact-email-label": "profile-form-label",
  "profile-form-contact-text-label": "profile-form-label",
  
  "prizes-list": "content-box",
  "prizes-raffle": "content-box",
  "prizes-raffle-title": "content-box-title",
  "prizes-list-title": "content-box-title",
}

CSS_CLASSES = {
  "user-post-avatar": "news-image",
  "user-post-content": "news-text",
  "user-post-date-string": "news-posted",
  "activity-categories-title": "activity-categories-title",
  
  "prize-item": "prize",
  "prize-number": "number",
  "prizes-add-button": "plus",
  "prizes-remove-button": "minus",
  "prize-dialog": "prize-dialog",
}
