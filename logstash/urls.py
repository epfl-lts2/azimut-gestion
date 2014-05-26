# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns(
    'logstash.views',

    url(r'^$', 'file_list'),
    url(r'^(?P<pk>[0-9]*)/show/$', 'file_show'),
    url(r'^(?P<pk>[0-9]*)/edit/$', 'file_edit'),
    url(r'^(?P<pk>[0-9]*)/delete/$', 'file_delete'),

    url(r'^(?P<name>.*)/shipper.conf$', 'generate_config'),

    url(r'^auto$', 'start_autodetect'),
    url(r'^auto/(?P<key>[0-9]*)$', 'watch_autodetect'),
    url(r'^auto/w/(?P<key>[0-9]*)$', 'watch_get_status'),
    url(r'^auto/confirm/(?P<key>[0-9]*)$', 'watch_final'),

)
