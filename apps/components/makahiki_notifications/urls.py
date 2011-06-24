from django.conf.urls.defaults import *

urlpatterns = patterns('components.makahiki_notifications.views',
    url(r'^(\d+)/read/$', 'read', name="notifications_read"),
)
