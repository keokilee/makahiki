from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'pages.mobile.views.index', name='mobile_index'),
    url(r'^landing/?$', 'pages.mobile.views.landing', name='mobile_landing'),
    url(r'^smartgrid/?$', 'pages.mobile.views.smartgrid', name='mobile_smartgrid'),
    url(r'^smartgrid/basicenrg/?$', 'pages.mobile.views.basicenrg', name='mobile_basic_enrg'),
    url(r'^smartgrid/getstarted/?$', 'pages.mobile.views.getstarted', name='mobile_get_started'),
    url(r'^smartgrid/movingon/?$', 'pages.mobile.views.movingon', name='mobile_moving_on'),
    url(r'^smartgrid/lightsout/?$', 'pages.mobile.views.lightsout', name='mobile_lights_out'),
    url(r'^smartgrid/makewatts/?$', 'pages.mobile.views.makewatts', name='mobile_make_watts'),
    url(r'^smartgrid/potpourri/?$', 'pages.mobile.views.potpourri', name='mobile_pot_pourri'),
    url(r'^smartgrid/opala/?$', 'pages.mobile.views.opala', name='mobile_opala'),
    url(r'^smartgrid/task/(\d+)/?$', 'pages.mobile.views.task', name='mobile_smartgrid_task'), 
    url(r'^smartgrid/task/(\d+)/form/?$', 'pages.mobile.views.sgform', name='mobile_smartgrid_form'),
    url(r'^smartgrid/task/(\d+)/form/add/?$', 'pages.mobile.views.sgadd', name='mobile_smartgrid_add'),
    url(r'^events/(\w*)/?$', 'pages.mobile.views.events', name='mobile_events'), 
    url(r'^quests/popup/?$', 'pages.mobile.views.popup', name='mobile_quest_popup'),
    url(r'^quests/(\w*)/?$', 'pages.mobile.views.quests', name='mobile_quests'),
    url(r'^quests/(?P<slug>[-\w]+)/?$', 'pages.mobile.views.quest_detail', name='mobile_quest_detail')
)
