from django.conf.urls.defaults import *

urlpatterns = patterns('pages.view_canopy.views',
    url(r'^$', 'index', name="canopy_index"),
    
    # Quest URLS
    url(r'^mission/(?P<slug>[-\w]+)/accept/$', 'mission_accept', name="canopy_mission_accept"),
    # url(r'^quest/(?P<slug>[-\w]+)/opt-out/$', 'quest_opt_out', name="canopy_quest_opt_out"),
    url(r'^mission/(?P<slug>[-\w]+)/cancel/$', 'mission_cancel', name="canopy_mission_cancel"),
    
    # Wall URLS
    url(r'^wall/post/$', 'post', name="canopy_wall_post"),
    url(r'^wall/more-posts/$', 'more_posts', name="canopy_more_posts"),
    
    # User Directory urls
    url(r'members/$', 'members', name="canopy_members"),
)
