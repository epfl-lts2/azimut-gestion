from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'', include('main.urls')),
    url(r'^servers/', include('servers.urls')),
    url(r'^groups/', include('groups.urls')),
    url(r'^keymanager/', include('keymanager.urls')),
    url(r'^portforwarding/', include('portforwarding.urls')),
    url(r'^hostnameforwarding/', include('hostnameforwarding.urls')),
    url(r'^backups/', include('backups.urls')),
    url(r'^proxmoxs/', include('proxmoxs.urls')),
    url(r'^fabrun/', include('fabrun.urls')),
    url(r'^wizards/', include('wizard.urls')),
    url(r'^samba/', include('samba.urls')),
    url(r'^logstash/', include('logstash.urls')),

    (r'^users/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    (r'^users/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),

    (r'^' + settings.MEDIA_URL[1:] + '(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),  # In prod, use apache !
    (r'^' + settings.STATIC_URL[1:] + '(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),  # In prod, use apache !
)
