# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns(
    'main.views',

    url(r'^$', 'home_redirect'),
    url(r'^home/$', 'home'),
    url(r'^about/me$', 'me'),

    url(r'^about/me/edit$', 'me_edit'),

    url(r'^about/me/password/$', 'me_password'),

    url(r'^users/$', 'users_list'),
    url(r'^users/(?P<pk>[0-9]*)/show/$', 'users_show'),
    url(r'^users/(?P<pk>[0-9]*)/edit/$', 'users_edit'),
    url(r'^users/(?P<pk>[0-9]*)/delete/$', 'users_delete'),
    url(r'^users/(?P<pk>[0-9]*)/password/$', 'users_setpassword'),

    url(r'^users/keys/add/(?P<pk>[0-9]*)$', 'users_keys_add'),
    url(r'^users/keys/delete/(?P<pk>[0-9]*)/(?P<keyPk>[0-9]*)$', 'users_keys_delete'),

    url(r'^keys/$', 'keys_list'),
    url(r'^keys/(?P<pk>[0-9]*)/show/$', 'keys_show'),
    url(r'^keys/(?P<pk>[0-9]*)/edit/$', 'keys_edit'),
    url(r'^keys/(?P<pk>[0-9]*)/delete/$', 'keys_delete'),

    url(r'^users/groups/add/(?P<pk>[0-9]*)$', 'users_groups_add'),
    url(r'^users/groups/delete/(?P<pk>[0-9]*)/(?P<groupPk>[0-9]*)$', 'users_groups_delete'),

    url(r'^users/servers/add/(?P<pk>[0-9]*)$', 'users_server_add'),
    url(r'^users/servers/delete/(?P<pk>[0-9]*)/(?P<serverPk>[0-9]*)$', 'users_server_delete'),

    url(r'^git_hook/(?P<id>.*)/$', 'git_hook'),
)
