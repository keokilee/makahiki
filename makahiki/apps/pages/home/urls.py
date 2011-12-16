from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'pages.home.views.index', name="home_index"),
    url(r'^restricted/$', 'pages.home.views.restricted', name="home_restricted"),
    url(r'^setup/welcome/$', 'pages.home.views.setup_welcome', name="setup_welcome"),
    url(r'^setup/terms/$', 'pages.home.views.terms', name="setup_terms"),
    url(r'^setup/referral/$', 'pages.home.views.referral', name='setup_referral'),
    url(r'^setup/profile/$', 'pages.home.views.setup_profile', name="setup_profile"),
    url(r'^setup/profile/facebook/$', 'pages.home.views.profile_facebook', name="setup_profile_facebook"),
    url(r'^setup/activity/$', 'pages.home.views.setup_activity', name="setup_activity"),
    url(r'^setup/question/$', 'pages.home.views.setup_question', name="setup_question"),
    url(r'^setup/complete/$', 'pages.home.views.setup_complete', name="setup_complete"),
    url(r'^tc/?$', 'pages.home.views.mobile_tc', name="mobile_tc"),
)
