# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns(
    'fabrun.views',

    url(r'^$', 'home'),
    url(r'^show/(?P<pk>[0-9]*)/$', 'show_run'),
)
