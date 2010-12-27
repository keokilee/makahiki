from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^rounds\.json$','api.views.rounds', name='api_rounds'),
    url(r'^standings/(?P<grouping>floor|individual)\.json$', 'api.views.standings', name="api_standings"),
)