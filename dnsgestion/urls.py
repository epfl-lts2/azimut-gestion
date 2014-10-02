# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns(
    'dnsgestion.views',

    url(r'^$', 'zones_list'),
    url(r'^(?P<pk>[0-9]*)/show/$', 'zones_show'),
    url(r'^(?P<pk>[0-9]*)/edit/$', 'zones_edit'),
    url(r'^(?P<pk>[0-9]*)/delete/$', 'zones_delete'),
    url(r'^(?P<pk>[0-9]*)/deploy/$', 'zones_deploy'),
    url(r'^(?P<pk>[0-9]*)/increment_and_deploy/$', 'zones_increment_and_deploy'),


    url(r'^entries/(?P<pk>[0-9]*)/edit/$', 'entry_edit'),
    url(r'^entries/(?P<pk>[0-9]*)/delete/$', 'entry_delete'),
    url(r'^entries/(?P<pk>[0-9]*)/up/$', 'entry_up'),
    url(r'^entries/(?P<pk>[0-9]*)/down/$', 'entry_down'),


    url(r'^config/(?P<pk>[0-9]*)/main/(?P<secret>.*)$', 'generate_main_file'),
    url(r'^config/(?P<pk>[0-9]*)/zone/(?P<secret>.*)$', 'generate_zone_file'),

)
