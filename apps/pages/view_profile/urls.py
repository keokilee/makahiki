from django.conf.urls.defaults import *

urlpatterns = patterns('',
    #url(r'^username_autocomplete/$', 'autocomplete_app.views.username_autocomplete_friends', name='profile_username_autocomplete'),
    #url(r'^username_autocomplete/$', 'autocomplete_app.views.username_autocomplete_all', name='profile_username_autocomplete'),
    #url(r'^$', 'makahiki_profiles.views.profiles', name='profile_list'),
    url(r'^$', 'pages.view_profile.views.index', name="profile_index"),
    url(r'^badges/$', 'pages.view_profile.views.badge_catalog', name="profile_badges"),
    url(r'^view_rejected/(\d+)/$', 'pages.view_profile.views.view_rejected', name="profile_rejected"),
)
