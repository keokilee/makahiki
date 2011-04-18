from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^accept/(\d+)/$', 'components.quests.views.accept', name="quests_accept"),
    url(r'^opt_out/(\d+)/$', 'components.quests.views.opt_out', name="quests_opt_out"),
    url(r'^cancel/(\d+)/$', 'components.quests.views.cancel', name="quests_cancel"),
)
