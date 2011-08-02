from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'pages.view_activities.views.index', name="activity_index"),

    # url(r'^task/(\d+)/$', 'pages.view_activities.views.task', name="activity_task"),
    url(r'^(?P<activity_type>[\w]+)/(?P<slug>[\w\d\-]+)/$', 'pages.view_activities.views.task', name='activity_task'),
    # url(r'^task/(\d+)/add$', 'pages.view_activities.views.add_task', name="activity_add_task"),
    url(r'^(?P<activity_type>[\w]+)/(?P<slug>[\w\d\-]+)/add/$', 'pages.view_activities.views.add_task', name='activity_add_task'),
    url(r'^(?P<activity_type>[\w]+)/(?P<slug>[\w\d\-]+)/drop/$', 'pages.view_activities.views.drop_task', name='activity_drop_task'),
    
    # url(r'^view_codes/(\d+)/$', 'pages.view_activities.views.view_codes', name="activity_view_codes"),
    url(r'^view-codes/(?P<slug>[\w\d\-]+)/$', 'pages.view_activities.views.view_codes', name='activity_view_codes'),

    url(r'^attend_code/$', 'pages.view_activities.views.attend_code', name="activity_attend_code"),
    url(r'^(?P<activity_type>[\w]+)/(?P<slug>[\w\d\-]+)/reminder/$', 'pages.view_activities.views.reminder', name='activity_reminder'),
    
    # url(r'^view_codes/(\d+)/$', 'pages.view_activities.views.view_codes', name="activity_view_codes"),
    url(r'^view-codes/(?P<slug>[\w\d\-]+)/$', 'pages.view_activities.views.view_codes', name='activity_view_codes'),
)
