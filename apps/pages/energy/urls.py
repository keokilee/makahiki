from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'pages.energy.views.index', name='help_index'),
)
