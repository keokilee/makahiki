from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^change_theme/$', 'makahiki_themes.views.change_theme'),
)
