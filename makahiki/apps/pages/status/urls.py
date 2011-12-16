from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'pages.status.views.home', name='status_home'),
    url(r'^points/$', 'pages.status.views.points_scoreboard', name='status_points'),
    url(r'^energy/$', 'pages.status.views.energy_scoreboard', name='status_energy'),
    url(r'^users/$', 'pages.status.views.users', name='status_users'),
    url(r'^prizes/$', 'pages.status.views.prizes', name='status_prizes'),
    url(r'^activities/$', 'pages.status.views.popular_activities', name='status_activities'),
    url(r'^rsvps/$', 'pages.status.views.event_rsvps', name='status_rsvps'),
)
