# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'backups.views',

    url(r'^$', 'backups_list'),
    url(r'^(?P<pk>[0-9]*)/show/$', 'backups_show'),
    url(r'^(?P<pk>[0-9]*)/edit/$', 'backups_edit'),
    url(r'^(?P<pk>[0-9]*)/delete/$', 'backups_delete'),
    url(r'^(?P<pk>[0-9]*)/run/$', 'backups_run'),
    url(r'^get_conf/(?P<pk>[0-9]*)/$', 'get_conf'),

    url(r'^clean_up$', 'clean_up'),

)
