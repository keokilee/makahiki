from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'pages.view_activities.views.index', name="activity_index"),
)
