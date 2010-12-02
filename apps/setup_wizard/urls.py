from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    url(r'^intro/$', direct_to_template, {"template": "setup_wizard/intro.html"}, name="setup_intro"),
    url(r'^terms/$', 'setup_wizard.views.terms', name='setup_terms'),
    url(r'^facebook/$', 'setup_wizard.views.facebook', name='setup_facebook'),
    url(r'^profile/$', 'setup_wizard.views.profile', name='setup_profile'),
)