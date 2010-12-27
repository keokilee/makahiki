from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^change_theme/$', 'components.makahiki_themes.views.change_theme'),
)
