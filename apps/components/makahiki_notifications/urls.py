from django.conf.urls.defaults import *

urlpatterns = patterns('components.makahiki_notifications.views',
    url(r'^read/(\d+)/$', 'read', name="notifications_read"),
)
