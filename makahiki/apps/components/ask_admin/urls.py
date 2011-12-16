from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^send-feedback/$', 
        'components.ask_admin.views.send_feedback', name="ask_admin_feedback"),
)
