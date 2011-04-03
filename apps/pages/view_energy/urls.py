from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'pages.view_energy.views.index', name='energy_index'),
    url(r'^post/$', 'pages.view_energy.views.post', name="energy_post"),

)
