from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'pages.canopy.views.index', name="canopy_index"),
)
