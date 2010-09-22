from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'mobile.views.index', name='mobile_index'),
    url(r'^login/$', 'mobile.views.login', name='mobile_login'),
    url(r'^home/$', 'mobile.views.profile', name='mobile_profile'),
)
