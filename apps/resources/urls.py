from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', "resources.views.index", name="resources_index"),
    url(r'^resource/(?P<resource_id>\d+)/$', 'resources.views.resource', name='resources_resource'),
    
    # AJAX XHR methods.
    url(r'^filter/$', "resources.views.filter", name="resources_filter"),
    url(r'^view_all/$', "resources.views.view_all", name="resources_all"),
)
