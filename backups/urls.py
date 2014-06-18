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
    url(r'^clean_up_old_sets$', 'clean_up_old_sets'),

    url(r'^runs$', 'backupsets_list'),
    url(r'^runs/(?P<pk>[0-9]*)/cancel$', 'backupsets_cancel'),

    url(r'^notifications$', 'backupnotifications_list'),
    url(r'^notifications/switch$', 'backupnotifications_switch'),
    url(r'^notifications/cleanup$', 'clean_up_notifications'),

    url(r'^zabbix/list/_$', 'zabbix_list'),
    url(r'^zabbix/last_hourly_duration/_$', 'zabbix_last_hourly_duration'),
    url(r'^zabbix/last_(?P<mode>(hourly|weekly|daily|monthly))/(?P<pk>[0-9]*)$', 'zabbix_last_nb_hours'),
    url(r'^zabbix/last_(?P<mode>(files|size))/(?P<pk>[0-9]*)$', 'zabbix_last_files_or_size'),
)
