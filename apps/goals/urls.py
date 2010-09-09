from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^vote/(?P<goal_id>\d+)/$', 'goals.views.vote', name='goal_vote'),
)
