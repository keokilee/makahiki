from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'pages.index.views.index', name='index_index'),
)
