from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'pages.landing.views.index', name='landing_index'),
)
