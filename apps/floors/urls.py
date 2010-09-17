from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^(?P<dorm_slug>[-\w]+)/floor/(?P<floor_slug>[-\w]+)/$', 
      'floors.views.floor', name='floor_detail'),
    url(r'^(?P<dorm_slug>[-\w]+)/floor/(?P<floor_slug>[-\w]+)/members/$', 
      'floors.views.floor_members', name='floor_members'),
    url(r'^(?P<dorm_slug>[-\w]+)/floor/(?P<floor_slug>[-\w]+)/wall_post/$', 
      'floors.views.wall_post', name='floor_post'),
)