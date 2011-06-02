from django.conf.urls.defaults import *

urlpatterns = patterns('',
  url(r'^$', 'pages.view_help.views.index', name='help_index'),
	url(r'^rules/(?P<slug>[\w\d\-]+)/$', 'pages.view_help.views.rules', name='help_rules_topic'),
	url(r'^faq/(?P<slug>[\w\d\-]+)/$', 'pages.view_help.views.faq', name='help_faq_topic'),
)
