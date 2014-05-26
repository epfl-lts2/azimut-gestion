# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404, HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.utils.encoding import smart_str
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.db import connections
from django.core.paginator import InvalidPage, EmptyPage, Paginator
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.contrib import messages

from servers.models import Server, ServerUser


@login_required
def home(request):
    """Show the information page"""

    servers = Server.objects.order_by('name').all()

    return render_to_response('keymanager/home.html', {'servers': servers, 'GESTION_URL': settings.GESTION_URL}, context_instance=RequestContext(request))


def get_keys(request, server, user):
    """Return keys for a server"""
    server = get_object_or_404(Server, keymanger_name=server)

    user = get_object_or_404(ServerUser, server=server, name=user)

    # List of groups
    groups = []

    for g in user.group_set.all():
        if g not in groups:
            groups.append(g)

    for g in server.groupwithaccess_set.all():
        if g not in groups:
            groups.append(g)

    # For each groups, build list of ssh keys
    ssh_keys = []

    for g in groups:
        for user in g.users.all():
            for key in user.sshkey_set.all():
                if key.key not in ssh_keys:
                    ssh_keys.append(key.key)

        for server in g.servers.all():
            for key in server.sshkey_set.all():
                if key.key not in ssh_keys:
                    ssh_keys.append(key.key)

        for key in g.servers_keys.all():
            if key.key not in ssh_keys:
                ssh_keys.append(key.key)

    # Allow each user who 'own' the server
    for user in server.users_owning_the_server.all():
        for key in user.sshkey_set.all():
            if key.key not in ssh_keys:
                ssh_keys.append(key.key)

    return render_to_response('keymanager/get_keys.html', {'ssh_keys': ssh_keys}, context_instance=RequestContext(request))
