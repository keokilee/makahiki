from django.conf.urls.defaults import *
from django.conf import settings

from django.views.generic.simple import direct_to_template

from account.openid_consumer import PinaxConsumer

from django.contrib import admin
admin.autodiscover()

import os

urlpatterns = patterns('',
    # some simple pages
    url(r'^$', direct_to_template, {"template": "homepage.html"}, name="home"),
    url(r'^billboard/$', direct_to_template, {"template": "billboard.html"}, name="billboard"),
    url(r'^about_us/$', direct_to_template, {"template": "about_us.html"}, name="about_us"),
    url(r'^kukui_cup/$', direct_to_template, {"template": "kukui_cup.html"}, name="kukui_cup"),
    url(r'^resources/dorm_energy/$', direct_to_template, {"template": "resources/dorm_energy.html"}, name="dorm_energy"),
    url(r'^resources/energy_hub/$', direct_to_template, {"template": "resources/energy_hub.html"}, name="energy_hub"),
    url(r'^resources/have_fun/$', direct_to_template, {"template": "resources/have_fun.html"}, name="have_fun"),
    url(r'^energy_data/day/$', direct_to_template, {"template": "energy_data/day.html"}, name="energy_day"),
    url(r'^energy_data/hour/$', direct_to_template, {"template": "energy_data/hour.html"}, name="energy_hour"),
    url(r'^energy_data/month/$', direct_to_template, {"template": "energy_data/month.html"}, name="energy_month"),
    url(r'^energy_data/real_time/$', direct_to_template, {"template": "energy_data/real_time.html"}, name="energy_real_time"),
    url(r'^energy_data/week/$', direct_to_template, {"template": "energy_data/week.html"}, name="energy_week"),
    
    # 3rd party
    (r'^frontendadmin/', include('frontendadmin.urls')),
    (r'^attachments/', include('attachments.urls')),
    
    # pinax provided
    (r'^account/', include('account.urls')),
    (r'^account/cas/login/$', 'django_cas.views.login'),
    (r'^account/cas/logout/$', 'django_cas.views.logout'),
    # (r'^openid/(.*)', PinaxConsumer()),
    (r'^avatar/', include('avatar.urls')),
    (r'^profiles/', include('kukui_cup_profile.urls')),
    (r'^admin/(.*)', admin.site.root),
)

if settings.SERVE_MEDIA:
    urlpatterns += patterns('',
        (r'^site_media/', include('staticfiles.urls')),
    )
