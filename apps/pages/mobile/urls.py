from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'pages.mobile.views.index', name='mobile_index'),
    url(r'^landing/$', 'pages.mobile.views.landing', name='mobile_landing'),
    url(r'^smartgrid/$', 'pages.mobile.views.smartgrid', name='mobile_smartgrid'),
    url(r'^smartgrid/task/(\d+)/$', 'pages.mobile.views.task', name='mobile_smartgrid_task'), 
    url(r'^events/(\w*)/$', 'pages.mobile.views.events', name='mobile_events'), 
    url(r'^smartgrid/task/(\d+)/response/$', 'pages.mobile.views.sgresponse', name='mobile_smartgrid_response'),
    url(r'^events/$', 'pages.mobile.views.events', name='mobile_events') 
)
