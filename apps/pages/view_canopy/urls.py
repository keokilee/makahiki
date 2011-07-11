from django.conf.urls.defaults import *

urlpatterns = patterns('pages.view_canopy.views',
    url(r'^$', 'index', name="canopy_index"),
    
    # Quest URLS
    url(r'^quest/(?P<slug>[-\w]+)/accept/$', 'quest_accept', name="canopy_quest_accept"),
    # url(r'^quest/(?P<slug>[-\w]+)/opt-out/$', 'quest_opt_out', name="canopy_quest_opt_out"),
    url(r'^quest/(?P<slug>[-\w]+)/cancel/$', 'quest_cancel', name="canopy_quest_cancel"),
    
    # Wall URLS
    url(r'^wall/post/$', 'post', name="canopy_wall_post"),
    url(r'^wall/more-posts/$', 'more_posts', name="canopy_more_posts"),
)
