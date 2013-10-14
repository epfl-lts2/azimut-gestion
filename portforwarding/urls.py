# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns(
    'portforwarding.views',

    url(r'^$', 'ports_list'),
    url(r'^(?P<pk>[0-9]*)/show/$', 'ports_show'),
    url(r'^(?P<pk>[0-9]*)/edit/$', 'ports_edit'),
    url(r'^(?P<pk>[0-9]*)/delete/$', 'ports_delete'),

    url(r'^get_script/(?P<pk>[0-9]*)/nat-vz$', 'get_script'),

    url(r'^(?P<pk>[0-9]*)/save_rom_server/$', 'save_from_server'),
    url(r'^(?P<pk>[0-9]*)/(?P<portPk>[0-9]*)/delete_from_server/$', 'delete_from_server'),

)
