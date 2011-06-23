from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'pages.mobile.views.index', name='mobile_index'),
    url(r'^landing/$', 'pages.mobile.views.landing', name='mobile_landing'),
    url(r'^smartgrid/$', 'pages.mobile.views.smartgrid', name='mobile_smartgrid'),
    url(r'^events/$', 'pages.mobile.views.events', name='mobile_events'),
    url(r'^events/sevent/$', 'pages.mobile.views.sevent', name='mobile_sevent')
)
