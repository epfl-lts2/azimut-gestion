# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns(
    'fabrun.views',

    url(r'^$', 'home'),
    url(r'^show/(?P<pk>[0-9]*)/$', 'show_run'),
    url(r'^clean_up$', 'clean_up'),
    url(r'^get_description$', 'get_description'),
    
)
