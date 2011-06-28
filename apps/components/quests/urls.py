from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^(?P<slug>[-\w]+)/accept/$', 'components.quests.views.accept', name="quests_accept"),
    url(r'^(?P<slug>[-\w]+)/opt-out/$', 'components.quests.views.opt_out', name="quests_opt_out"),
    url(r'^(?P<slug>[-\w]+)/cancel/$', 'components.quests.views.cancel', name="quests_cancel"),
)
