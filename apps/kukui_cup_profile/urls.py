from django.conf.urls.defaults import *

urlpatterns = patterns('',
    #url(r'^username_autocomplete/$', 'autocomplete_app.views.username_autocomplete_friends', name='profile_username_autocomplete'),
    #url(r'^username_autocomplete/$', 'autocomplete_app.views.username_autocomplete_all', name='profile_username_autocomplete'),
    #url(r'^$', 'kukui_cup_profile.views.profiles', name='profile_list'),
    url(r'^profile/(?P<username>[\w\._-]+)/$', 'kukui_cup_profile.views.profile', name='profile_detail'),
    url(r'^edit/$', 'kukui_cup_profile.views.profile_edit', name='profile_edit'),
)
