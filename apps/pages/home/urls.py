from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'pages.home.views.index', name="home_index"),
    url(r'^setup/welcome/$', 'pages.home.views.setup_welcome', name="setup_welcome"),
    url(r'^setup/terms/$', 'pages.home.views.terms', name="setup_terms"),
    url(r'^setup/facebook/$', 'pages.home.views.facebook_connect', name="setup_facebook"),
)
