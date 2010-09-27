from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^(?P<item_type>activity|commitment)_list/$', 'activities.views.list', name="activity_list"),
    url(r'^(?P<item_type>activity|commitment)_detail/(?P<item_id>\d+)/$', 'activities.views.detail', name="activity_detail"),
    
    # Actions
    url(r'^like_(?P<item_type>activity)/(?P<item_id>\d+)/$', 
      'activities.views.like', name='activity_like'),
    url(r'^unlike_(?P<item_type>activity)/(?P<item_id>\d+)/$', 
      'activities.views.unlike', name='activity_unlike'),
    url(r'^add_(?P<item_type>activity|commitment)/(?P<item_id>\d+)/$',
      'activities.views.add_participation', name='add_participation'),
    url(r'^remove_(?P<item_type>activity|commitment)/(?P<item_id>\d+)/$',
      'activities.views.remove_participation', name='remove_participation'),
    url(r'^request_(?P<item_type>activity|commitment)_points/(?P<item_id>\d+)/$',
      'activities.views.request_points', name='request_points'),
    url(r'^view_codes/(?P<activity_id>\d+)/$', 'activities.views.view_codes', name='view_codes')
)
