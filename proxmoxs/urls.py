# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns(
    'proxmoxs.views',

    url(r'^$', 'vms_list'),
    url(r'^(?P<serverPk>[0-9]*)/(?P<vmId>[0-9]*)/delete/$', 'vms_delete'),
    url(r'^(?P<serverPk>[0-9]*)/(?P<vmId>[0-9]*)/stop/$', 'vms_stop'),
    url(r'^(?P<serverPk>[0-9]*)/(?P<vmId>[0-9]*)/start/$', 'vms_start'),
    url(r'^(?P<serverPk>[0-9]*)/create/$', 'vms_create'),
    url(r'^(?P<serverPk>[0-9]*)/(?P<vmId>[0-9]*)/update/$', 'vms_update'),
)
