from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # some simple pages
    url(r'^$', "resources.views.index", name="resources_index"),
    url(r'^topic/(?P<topic_id>\d+)/$', 'resources.views.topic', name='resources_topic'),
    url(r'^resource/(?P<resource_id>\d+)/$', 'resources.views.resource', name='resources_resource'),
)
