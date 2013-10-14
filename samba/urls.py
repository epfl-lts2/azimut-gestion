# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns(
    'samba.views',

    url(r'^$', 'shares_list'),
    url(r'^(?P<pk>[0-9]*)/show/$', 'shares_show'),
    url(r'^(?P<pk>[0-9]*)/edit/$', 'shares_edit'),
    url(r'^(?P<pk>[0-9]*)/delete/$', 'shares_delete'),

    url(r'^(?P<pk>[0-9]*)/config/$', 'get_config'),

)
