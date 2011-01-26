# default.py
#
# This file maps ids to a string of classes.  Templates that use class_tags and insert_classes refer to this file.
# Note that some of the "ids" are more like css selectors.

# If True, the classes will be inserted.  Otherwise, the tags will be empty strings.
RETURN_CLASSES = True

CSS_CLASSES = {
  "profile-left": "span-8",
  "profile-middle": "span-8",
  "profile-right": "span-8 last",
  "widget": "widget ui-corner-all ui-accordion ui-widget ui-accordion-icons",
  "widget-title": "widget-title ui-state-active ui-accordion-header ui-corner-top",
  "widget-body": "widget-body ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom ui-accordion-content-active",
  "ui-button": "ui-button ui-state-default ui-corner-all",
  
  "energy-left": "span-6",
  "energy-right": "span-18 last",
  
  "activity-left": "span-9",
  "activity-right": "span-15 last",
  "activity-category": "ui-accordion-content ui-widget-content ui-corner-all ui-accordion-content-active",
}