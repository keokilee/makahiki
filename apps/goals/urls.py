from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^vote/(?P<goal_id>\d+)/$', 'goals.views.vote', name='goal_vote'),
    url(r'^vote/(?P<goal_id>\d+)/results/$', 'goals.views.voting_results', name='goal_vote_results'),
)
