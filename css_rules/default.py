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
  "canopy": '<link rel="stylesheet" href="{0}css/{1}/pages/canopy.css">',
}
CSS_IDS = {
  "landing-sponsors": "content-box",
  "landing-sponsors-title": "content-box-title",
  
  "quest-list": "quest-list",
  
  "home-energy": "home-item",
  "home-activities": "home-item",
  "home-news": "home-item",
  "home-prizes": "home-item",
  "home-help": "home-item",
  "home-profile": "home-item",
  
  "energy-power": "content-box",
  "energy-scoreboard-box": "content-box",
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
  "news-members": "content-box",
  "news-wall-title": "content-box-title",
  "news-events-title": "content-box-title",
  "news-commitments-title": "content-box-title",
  "news-most-popular-title": "content-box-title",
  "news-members-title": "content-box-title",
  "floor-members": "content-box",
  "floor-members-title": "content-box-title",
  
  "help-video": "content-box",
  "help-rules": "content-box",
  "help-faq": "content-box",
  "help-ask": "content-box",
  "help-topic": "content-box",
  "help-video-title": "content-box-title",
  "help-rules-title": "content-box-title",
  "help-faq-title": "content-box-title",
  "help-ask-title": "content-box-title",
  "help-topic-title": "content-box-title",
  "help-video-content": "content-box-contents",
  "help-rules-content": "content-box-contents",
  "help-faq-content": "content-box-contents",
  "help-topic-content": "content-box-contents",
  
  "profile-form-box": "content-box",
  "profile-badges-box": "content-box",
  "profile-history-box": "content-box",
  "profile-commitments-box": "content-box",
  "profile-notifications-box": "content-box",
  "profile-form-title": "content-box-title",
  "profile-badges-title": "content-box-title",
  "profile-history-title": "content-box-title",
  "profile-notifications-title": "content-box-title",
  "profile-commitments-title": "content-box-title",
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
  
  "badge-catalog-box": "content-box",
  "badge-catalog-title": "content-box-title",
  
  "avatar-change": "content-box",
  "avatar-change-title": "content-box-title",
  
  "prizes-list": "content-box",
  "prizes-raffle": "content-box",
  "prizes-raffle-title": "content-box-title",
  "prizes-list-title": "content-box-title",
  
  "canopy-quests": "content-box",
  "canopy-quests-title": "content-box-title",
  "canopy-viz": "content-box",
  "canopy-viz-title": "content-box-title",
  "canopy-feed": "content-box",
  "canopy-feed-title": "content-box-title",
  "canopy-members": "content-box",
  "canopy-members-title": "content-box-title",
}

CSS_CLASSES = {
  "system-post": "news-system-post",
  "system-post-date-string": "news-system-posted",
  "system-post-content": "news-system-text",
  "user-post-avatar": "news-image",
  "user-post-content": "news-text",
  "user-post-date-string": "news-posted",
  "activity-categories-title": "activity-categories-title",
  "prize-item": "prize",
  "prize-number": "number",
  "prize-dialog": "prize-dialog",
}
