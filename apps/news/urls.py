from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^(?P<item_id>\d+)/((?P<slug>[-\w]+)/)?$',
      'news.views.article', name='view_article'),
)