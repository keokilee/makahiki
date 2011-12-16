from django.conf.urls.defaults import *

urlpatterns = patterns('pages.view_prizes.views',
    url(r'^$', 'index', name='prizes_index'),
    url(r'^raffle/(\d+)/add_ticket/$', 'add_ticket', name="raffle_add_ticket"),
    url(r'^raffle/(\d+)/remove_ticket/$', 'remove_ticket', name="raffle_remove_ticket"),
    url(r'^raffle/(\d+)/view-form/$', 'raffle_form', name="raffle_view_form"),
)
