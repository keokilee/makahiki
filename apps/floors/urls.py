from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^(?P<dorm_slug>[-\w]+)/$', 'floors.views.dorm', name='dorm'),
    url(r'^(?P<dorm_slug>[-\w]+)/floor/(?P<floor>)\d+/$', 'floors.views.floor', name='floor'),
)