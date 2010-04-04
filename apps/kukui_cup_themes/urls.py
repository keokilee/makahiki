from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^change_theme/$', 'kukui_cup_themes.views.change_theme'),
)
