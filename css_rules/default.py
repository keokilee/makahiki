# default.py
#
# This file maps ids to a string of classes.  Templates that use class_tags and insert_classes refer to this file.
# Note that some of the "ids" are more like class names.  These rules act like "macro expansions" in the templates.

# If True, the classes will be inserted.  Otherwise, the tags will be empty strings.
RETURN_CLASSES = True

CSS_IMPORTS = """
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

<script type="text/javascript" src="http://www.google.com/jsapi"></script>
<script type="text/javascript" src="http://wattdepot-gdata.googlecode.com/svn/trunk/javascript/ajile/com.iskitz.ajile.js?mvcoff,mvcshareoff,refresh"></script>
<script type="text/javascript" src="http://wattdepot-gdata.googlecode.com/svn/trunk/javascript/org.wattdepot.gdata.GDataLoader.js"></script>
<script type="text/javascript" src="http://wattdepot-gdata.googlecode.com/svn/trunk/javascript/org.wattdepot.gdata.kukuicup.Configuration.js"></script>
<script type="text/javascript" src="http://wattdepot-gdata.googlecode.com/svn/trunk/javascript/org.wattdepot.gdata.makahiki.EnergyRank.js"></script>
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

}

CSS_CLASSES = {
  "user-post-avatar": "news-image",
  "user-post-content": "news-text",
  "user-post-date-string": "news-posted",
  "activity-categories-title": "activity-categories-title",
  
}
