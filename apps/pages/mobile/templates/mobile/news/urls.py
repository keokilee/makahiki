from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'views.news', name='news_index') 
)
