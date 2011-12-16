from django.conf.urls.defaults import *

urlpatterns = patterns('pages.view_help.views',
  url(r'^$', 'index', name='help_index'),
	url(r'^(?P<category>\w+)/(?P<slug>[\w\d\-]+)/$', 'topic', name='help_topic'),
)
