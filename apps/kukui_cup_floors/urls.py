from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^(?P<dorm_slug>[-\w]+)/$', 'kukui_cup_floors.views.dorm', name='dorm'),
    url(r'^(?P<dorm_slug>[-\w]+)/floor/(?P<floor>)\d+/$', 'kukui_cup_floors.views.floor', name='floor'),
)