from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('kukui_cup_avatar.views',
    url('^change/$', 'change', name='avatar_change'),
    url('^delete/$', 'delete', name='avatar_delete'),
)
