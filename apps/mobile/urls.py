from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'mobile.views.index', name='mobile_index'),
)
