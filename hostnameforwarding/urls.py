# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns(
    'hostnameforwarding.views',

    url(r'^$', 'hosts_list'),
    url(r'^(?P<pk>[0-9]*)/show/$', 'hosts_show'),
    url(r'^(?P<pk>[0-9]*)/edit/$', 'hosts_edit'),
    url(r'^(?P<pk>[0-9]*)/delete/$', 'hosts_delete'),

    url(r'^get_conf/(?P<pk>[0-9]*)/ngnix.conf$', 'get_conf'),

    url(r'^(?P<pk>[0-9]*)/save_rom_server/$', 'save_from_server'),
    url(r'^(?P<pk>[0-9]*)/(?P<portPk>[0-9]*)/delete_from_server/$', 'delete_from_server'),

)
