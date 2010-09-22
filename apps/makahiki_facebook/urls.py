from django.conf.urls.defaults import *

# Hack to get the project name
project = __name__.split('.')[0]

# You'd want to change this to wherever your app lives
urlpatterns = patterns('',
    # Some functionality - users can post text to their homepage
    (r'^canvas/post/', 'makahiki_facebook.views.post'),

    # For the mock AJAX functionality
    (r'^canvas/ajax/', 'makahiki_facebook.views.ajax'),

    # This is the canvas callback, i.e. what will be seen
    # when you visit http://apps.facebook.com/<appname>.
    (r'^canvas/', 'makahiki_facebook.views.canvas'),

    # Extra callbacks can be set in the Facebook app settings
    # page. For example, post_add will be called when a user
    # has added the application.
    (r'^post_add/', 'makahiki_facebook.views.post_add'),

)
