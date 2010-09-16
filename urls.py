from django.conf.urls.defaults import *
from django.conf import settings

from django.views.generic.simple import direct_to_template

from account.openid_consumer import PinaxConsumer

from django.contrib import admin
admin.autodiscover()

import os

urlpatterns = patterns('',
    # some simple pages
    url(r'^$', "makahiki_base.views.index", name="index"),
    url(r'^home/$', "makahiki_base.views.homepage", name="home"),
    url(r'^billboard/$', direct_to_template, {"template": "billboard.html"}, name="billboard"),
    url(r'^about_us/$', direct_to_template, {"template": "about_us.html"}, name="about_us"),
    url(r'^rules/$', direct_to_template, {"template": "rules.html"}, name="rules"),
    url(r'^standings/', include('standings.urls')),
    url(r'^resources/', include('resources.urls')),
    url(r'^energy_data/$', "energy_data.views.index", name="energy_data"),
    
    # Kukui Cup Provided
    (r'^profiles/', include('makahiki_profiles.urls')),
    (r'^activities/', include('activities.urls')),
    (r'^themes/', include('makahiki_themes.urls')),
    (r'^news/', include('makahiki_base.urls')),
    (r'^dorms/', include('floors.urls')),
    (r'^api/', include('api.urls')),
    (r'^goals/', include('goals.urls')),
    
    # 3rd party
    (r'^frontendadmin/', include('frontendadmin.urls')),
    (r'^attachments/', include('attachments.urls')),
    
    # pinax provided
    (r'^account/', include('account.urls')),
    (r'^account/cas/login/$', 'django_cas.views.login'),
    (r'^account/cas/logout/$', 'django_cas.views.logout'),
    # (r'^openid/(.*)', PinaxConsumer()),
    (r'^avatar/', include('makahiki_avatar.urls')),
    (r'^admin/(.*)', admin.site.root),
    # (r'^notifications/', include('notification.urls')),
    
    # Facebook Connect
    # (r'^facebook/', include('facebookconnect.urls')),
)

if settings.SERVE_MEDIA:
    urlpatterns += patterns('',
        (r'^site_media/', include('staticfiles.urls')),
    )
