from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^(?P<obj_type>\w+)/(?P<obj>[\w\d\-]+)/(?P<action>[\w\d\-]+)/$', 
        'components.logging.views.log_ajax', name="logger_log_ajax"),
)
