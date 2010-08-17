from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^rounds\.json$','api.views.rounds', name='api_rounds'),
)