from django.conf.urls.defaults import *

urlpatterns = patterns('',
    #url(r'^username_autocomplete/$', 'autocomplete_app.views.username_autocomplete_friends', name='profile_username_autocomplete'),
    #url(r'^username_autocomplete/$', 'autocomplete_app.views.username_autocomplete_all', name='profile_username_autocomplete'),
    #url(r'^$', 'makahiki_profiles.views.profiles', name='profile_list'),
    url(r'^my_profile/$', 'makahiki_profiles.views.user_profile', name="user_profile"),
    url(r'^profile/(?P<user_id>\d+)/$', 'makahiki_profiles.views.profile', name='profile_detail'),
    url(r'^edit/$', 'makahiki_profiles.views.profile_edit', name='profile_edit'),
)
