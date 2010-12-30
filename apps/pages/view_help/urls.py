from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'pages.view_help.views.index', name='help_index'),
)
