# default.py
#
# This file maps ids to a string of classes.  Templates that use class_tags and insert_classes refer to this file.
# Note that some of the "ids" are more like class names.  These rules act like "macro expansions" in the templates.

# If True, the classes will be inserted.  Otherwise, the tags will be empty strings.
RETURN_CLASSES = True

CSS_CLASSES = {
  "home-energy": "span-11",
  "home-activities": "span-11 prepend-1 last",
  "home-news": "span-6 prepend-2",
  "home-prizes": "span-6 prepend-7 last",
  "home-learn": "span-6 prepend-5",
  "home-profile": "span-6 prepend-1 last",
  
  "news-events+popular+activities": "span-8",
  "news-wall": "span-15 prepend-1 last",
  
  "profile-form": "span-8",
  "profile-badges": "span-8",
  "profile-history": "span-8 last",
  
  "landing-logo": "span-3",
  "landing-title": "span-21 last",
  "landing-intro": "span-12",
  "landing-poster": "span-12 last",
  "landing-page": "span-24 last",
  "landing-button": "ui-button ui-widget ui-corner-all ui-state-active",
  
  "energy-power+scoreboard": "span-6",
  "energy-status": "span-18 last",
  
  "activity-events+scoreboard": "span-9",
  "activity-categories": "span-15 last",
  "activity-category": "ui-accordion-content ui-widget-content ui-corner-all ui-accordion-content-active",
  
  "help-video": "span-8",
  "help-rules": "span-7 prepend-1",
  "help-faq": "span-7 prepend-1 last",
  "help-ask": "span-15 prepend-9 last",
  
  "prizes-list": "span-11",
  "prizes-raffle": "span-13 last",
  "prizes-add-button": "ui-button ui-state-default ui-corner-all",
  "prizes-remove-button": "ui-button ui-state-error ui-corner-all",
  "prizes-disabled-button": "ui-button ui-state-disabled ui-corner-all",
  "prizes-info": "span-10 last",
  
  "widget": "widget ui-corner-all ui-accordion ui-widget ui-accordion-icons",
  "widget-title": "widget-title ui-state-active ui-accordion-header ui-corner-top",
  "widget-body": "widget-body ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom ui-accordion-content-active",
  "ui-button": "ui-button ui-state-default ui-corner-all",
}