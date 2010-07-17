from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', "resources.views.index", name="resources_index"),
    url(r'^resource/(?P<resource_id>\d+)/$', 'resources.views.resource', name='resources_resource'),
)
