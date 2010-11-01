from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^terms/$', 'setup_wizard.views.terms', name='setup_terms'),
    url(r'^facebook/$', 'setup_wizard.views.facebook', name='setup_facebook'),
)