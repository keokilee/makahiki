from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'pages.mobile.views.index', name='mobile_index'),
    url(r'^login/$', 'pages.mobile.views.login', name='mobile_login'),
    url(r'^home/$', 'pages.mobile.views.profile', name='mobile_profile'),
)
