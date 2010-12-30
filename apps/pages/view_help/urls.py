from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'pages.help.views.index', name='help_index'),
)
