# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns(
    'servers.views',


    url(r'^$', 'servers_list'),

    url(r'^map$', 'servers_map'),



    url(r'^(?P<pk>[0-9]*)/show/$', 'servers_show'),
    url(r'^(?P<pk>[0-9]*)/edit/$', 'servers_edit'),
    url(r'^(?P<pk>[0-9]*)/delete/$', 'servers_delete'),

    url(r'^keys/add/(?P<pk>[0-9]*)$', 'servers_keys_add'),
    url(r'^keys/delete/(?P<pk>[0-9]*)/(?P<keyPk>[0-9]*)$', 'servers_keys_delete'),

    url(r'^keys/$', 'keys_list'),
    url(r'^keys/(?P<pk>[0-9]*)/show/$', 'keys_show'),
    url(r'^keys/(?P<pk>[0-9]*)/edit/$', 'keys_edit'),
    url(r'^keys/(?P<pk>[0-9]*)/delete/$', 'keys_delete'),

    url(r'^groups/add/(?P<pk>[0-9]*)$', 'servers_groups_add'),
    url(r'^groups/delete/(?P<pk>[0-9]*)/(?P<groupPk>[0-9]*)$', 'servers_groups_delete'),
    url(r'^groups/delete/(?P<pk>[0-9]*)/(?P<groupPk>[0-9]*)/(?P<keyPk>[0-9]*)$', 'servers_groups_key_delete'),


    url(r'^groupsaccess/add/(?P<pk>[0-9]*)$', 'servers_groupsaccess_add'),
    url(r'^groupsaccess/delete/(?P<pk>[0-9]*)/(?P<groupPk>[0-9]*)$', 'servers_groupsaccess_delete'),
    url(r'^groupsaccess/delete/(?P<pk>[0-9]*)/(?P<groupPk>[0-9]*)/(?P<userPk>[0-9]*)$', 'servers_groupsaccess_user_delete'),

)
