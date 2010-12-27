from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^((?P<dorm_slug>[-\w]+)/)?$', "standings.views.index", name="standings"),
)
