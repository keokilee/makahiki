from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^(?P<dorm_slug>[-\w]+)/$', 'floors.views.dorm', name='dorm_detail'),
    url(r'^(?P<dorm_slug>[-\w]+)/floor/(?P<floor_slug>[-\w]+)/$', 'floors.views.floor', name='floor_detail'),
)