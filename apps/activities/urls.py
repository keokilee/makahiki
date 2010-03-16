from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^add_commitment/(?P<commitment_id>\d+)/$', 'activities.views.add_commitment', name='add_commitment'),
    url(r'^remove_commitment/(?P<commitment_id>\d+)/$', 'activities.views.remove_commitment', name='remove_commitment'),
)
