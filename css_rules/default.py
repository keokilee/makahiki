# default.py
#
# This file maps ids to a string of classes.  Templates that use class_tags and insert_classes refer to this file.
# Note that some of the "ids" are more like class names.  These rules act like "macro expansions" in the templates.

# If True, the classes will be inserted.  Otherwise, the tags will be empty strings.
RETURN_CLASSES = True

CSS_CLASSES = {
  "home-top-left": "span-11",
  "home-top-right": "span-11 prepend-1 last",
  "home-middle-left": "span-6 prepend-2",
  "home-middle-right": "span-6 prepend-7 last",
  "home-bottom-left": "span-6 prepend-5",
  "home-bottom-right": "span-6 prepend-1 last",
  
  "news-left": "span-8",
  "news-right": "span-15 prepend-1 last",
  
  "profile-left": "span-8",
  "profile-middle": "span-8",
  "profile-right": "span-8 last",
  
  "widget": "widget ui-corner-all ui-accordion ui-widget ui-accordion-icons",
  "widget-title": "widget-title ui-state-active ui-accordion-header ui-corner-top",
  "widget-body": "widget-body ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom ui-accordion-content-active",
  "ui-button": "ui-button ui-state-default ui-corner-all",
  
  "landing-logo": "span-3",
  "landing-title": "span-21 last",
  "landing-intro": "span-12",
  "landing-poster": "span-12 last",
  "landing-page": "span-24 last",
  "landing-button": "ui-button ui-widget ui-corner-all ui-state-active",
  
  "energy-left": "span-6",
  "energy-right": "span-18 last",
  
  "activity-left": "span-9",
  "activity-right": "span-15 last",
  "activity-category": "ui-accordion-content ui-widget-content ui-corner-all ui-accordion-content-active",
}