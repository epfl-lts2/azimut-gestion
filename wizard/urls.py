# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns(
    'wizard.views',

    url(r'^$', 'home'),
    url(r'^s/(?P<uid>.*)/$', 'do_step'),
    url(r'^t/(?P<uid>.*)/$', 'do_tasks'),
    url(r'^ts/(?P<pk>.*)/$', 'get_task_status'),

)
