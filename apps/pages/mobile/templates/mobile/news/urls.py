from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'views.news', name='news_index'),
    url(r'^(\d+)/?$', 'views.more_posts', name='news_more')
)
