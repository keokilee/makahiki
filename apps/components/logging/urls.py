from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^log/$', 'components.logging.views.log_action', name="logger_log_action"),
)
