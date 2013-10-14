# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns(
    'groups.views',

    url(r'^$', 'groups_list'),
    url(r'^(?P<pk>[0-9]*)/show/$', 'groups_show'),
    url(r'^(?P<pk>[0-9]*)/edit/$', 'groups_edit'),
    url(r'^(?P<pk>[0-9]*)/delete/$', 'groups_delete'),

)
