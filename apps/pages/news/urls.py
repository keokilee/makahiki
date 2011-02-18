from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'pages.news.views.index', name='news_index'),
    url(r'^more_posts/$', 'pages.news.views.more_posts', name='news_more_posts'),
)
