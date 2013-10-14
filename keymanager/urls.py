# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns(
    'keymanager.views',

    url(r'^$', 'home'),
    url(r'^servers/getKeys/(?P<server>.*)/(?P<user>.*)/$', 'get_keys'),

)
