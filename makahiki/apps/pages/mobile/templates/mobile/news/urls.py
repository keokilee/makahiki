from django.conf.urls.defaults import *

urlpatterns = patterns('',  
    url(r'^$', 'pages.mobile.templates.mobile.news.views.news', name='mobile_news_index'),
    url(r'^(\d+)/?$', 'pages.mobile.templates.mobile.news.views.more_posts', name='mobile_news_more'),
    url(r'^post/$', 'pages.mobile.templates.mobile.news.views.post', name="mobile_news_post"),
)
