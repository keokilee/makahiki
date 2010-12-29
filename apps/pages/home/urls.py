from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'pages.home.views.index', name='help_index'),
)
