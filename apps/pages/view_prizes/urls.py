from django.conf.urls.defaults import *

urlpatterns = patterns('pages.view_prizes.views',
    url(r'^$', 'index', name='prizes_index'),
)
