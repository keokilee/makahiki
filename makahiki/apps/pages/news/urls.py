from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'pages.news.views.index', name='news_index'),
    url(r'^more_posts/$', 'pages.news.views.more_posts', name='news_more_posts'),
    url(r'^post/$', 'pages.news.views.post', name="news_post"),
    url(r'^popular-tasks/$', 'pages.news.views.get_popular_tasks', name="news_popular_tasks"),
    url(r'^floor-members/$', 'pages.news.views.floor_members', name="news_floor_members"),
)
