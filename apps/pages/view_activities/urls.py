from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'pages.view_activities.views.index', name="activity_index"),
    
    url(r'^category/(\d+)/$', 'pages.view_activities.views.category', name="activity_category"),
    url(r'^task/(\w+)/(\d+)/$', 'pages.view_activities.views.task', name="activity_task"),
    url(r'^task/(\w+)/(\d+)/add$', 'pages.view_activities.views.add_task', name="activity_add_task"),
    
    url(r'^view_codes/(\d+)/$', 'pages.view_activities.views.view_codes', name="activity_view_codes"),
    
)
