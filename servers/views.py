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

from servers.models import Server, SshKey, ServerUser
from servers.forms import ServerForm, ServerSshKey, SshKeyForm
from groups.models import Group
from django.contrib.auth.models import User


@login_required
def servers_list(request):
    """Show the list of servers"""

    if request.user.is_staff:
        liste = Server.objects.order_by('-is_vm', 'vm_host__name', 'name').all()
    else:
        liste = Server.objects.order_by('-is_vm', 'vm_host__name', 'name').filter(users_owning_the_server=request.user).all()

    return render_to_response('servers/servers/list.html', {'liste': liste}, context_instance=RequestContext(request))


@login_required
def servers_show(request, pk):
    """Show details of an Server"""

    object = get_object_or_404(Server, pk=pk)

    if not request.user.is_staff and not request.user in object.users_owning_the_server.all():
        raise Http404

    groups = Group.objects.order_by('name').all()

    return render_to_response('servers/servers/show.html', {'object': object, 'groups': groups}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def servers_edit(request, pk):
    """Edit an server"""

    try:
        object = Server.objects.get(pk=pk)
    except:
        object = Server()

    if request.method == 'POST':  # If the form has been submitted...
        form = ServerForm(request.POST, instance=object)

        users = request.POST.get('users')

        if form.is_valid():  # If the form is valid
            object = form.save()

            toadd_users = users.split(',')

            for u in object.serveruser_set.all():
                if u.name in toadd_users:
                    toadd_users.remove(u.name)
                else:
                    u.delete()

            for u in toadd_users:
                ServerUser(server=object, name=u).save()

            messages.success(request, 'The server has been saved.')

            return redirect(reverse('servers.views.servers_list'))
    else:
        form = ServerForm(instance=object)

        users = ''

        if object.pk:
            for u in object.serveruser_set.all():
                users += u.name + ','

        users = users[:-1]  # Remove last ,

    all_users = ['root']

    for u in User.objects.order_by('username').all():
        all_users.append(u.username)

    return render_to_response('servers/servers/edit.html', {'form': form, 'users': users, 'all_users': all_users}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def servers_delete(request, pk):
    """Delete an server"""

    object = get_object_or_404(Server, pk=pk)

    object.delete()

    messages.success(request, 'Server has been deleted.')

    return redirect(reverse('servers.views.servers_list', args=()))


@login_required
@staff_member_required
def servers_keys_add(request, pk):

    server = get_object_or_404(Server, pk=pk)

    baseKey = SshKey(server=server)

    if request.method == 'POST':  # If the form has been submitted...
        form = ServerSshKey(instance=baseKey, data=request.POST)

        if form.is_valid():  # If the form is valid
            form.save()

            messages.success(request, 'The ssh key has been added.')

            if pk:
                return redirect(reverse('servers.views.servers_show', args=(pk, )))
            else:
                return redirect(reverse('servers.views.me',))
    else:
        form = ServerSshKey(instance=baseKey)

    return render_to_response('servers/add_ssh.html', {'form': form, 'ownMode': not pk}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def servers_keys_delete(request, pk, keyPk):
    """Delete a server key"""

    server = get_object_or_404(Server, pk=pk)

    baseKey = get_object_or_404(SshKey, server=server, pk=keyPk)

    baseKey.delete()

    messages.success(request, 'The ssh key has been deleted.')

    return redirect(reverse('servers.views.servers_show', args=(pk, )))


@login_required
@staff_member_required
def keys_list(request):
    """Show the list of keys"""

    liste = SshKey.objects.order_by('server__name').all()

    return render_to_response('servers/keys/list.html', {'liste': liste}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def keys_show(request, pk):
    """Show details of an ssk key"""

    object = get_object_or_404(SshKey, pk=pk)

    return render_to_response('servers/keys/show.html', {'object': object}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def keys_edit(request, pk):
    """Edit an ssh key"""

    try:
        object = SshKey.objects.get(pk=pk)
    except:
        object = SshKey()

    if request.method == 'POST':  # If the form has been submitted...
        form = SshKeyForm(request.POST, instance=object)

        if form.is_valid():  # If the form is valid
            object = form.save()

            messages.success(request, 'The ssh key has been saved.')

            return redirect(reverse('servers.views.keys_list'))
    else:
        form = SshKeyForm(instance=object)

    return render_to_response('servers/keys/edit.html', {'form': form}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def keys_delete(request, pk):
    """Delete an ssh key"""

    object = get_object_or_404(SshKey, pk=pk)

    object.delete()

    messages.success(request, 'The ssh key has been deleted.')

    return redirect(reverse('servers.views.keys_list', args=()))


@login_required
@staff_member_required
def servers_groups_add(request, pk):
    """Add a server into a group"""

    server = get_object_or_404(Server, pk=pk)

    group = get_object_or_404(Group, pk=request.GET.get('groupPk'))

    key_pk = request.GET.get('keyPk')

    if key_pk == '0':
        group.servers.add(server)
        messages.success(request, 'The server has been added to the group (all keys).')
    else:
        key = get_object_or_404(SshKey, pk=key_pk, server=server)
        group.servers_keys.add(key)
        messages.success(request, 'The server has been added to the group (' + key.__unicode__() + ').')

    return redirect(reverse('servers.views.servers_show', args=(server.pk, )))


@login_required
@staff_member_required
def servers_groups_delete(request, pk, groupPk):
    """Delete a server from a group"""

    server = get_object_or_404(Server, pk=pk)

    group = get_object_or_404(Group, pk=groupPk)

    group.servers.remove(server)

    messages.success(request, 'The server has been removed from the group.')

    return redirect(reverse('servers.views.servers_show', args=(server.pk, )))


@login_required
@staff_member_required
def servers_groups_key_delete(request, pk, groupPk, keyPk):
    """Delete a server key from a group"""

    server = get_object_or_404(Server, pk=pk)

    key = get_object_or_404(SshKey, pk=keyPk, server=server)

    group = get_object_or_404(Group, pk=groupPk)

    group.servers_keys.remove(key)

    messages.success(request, 'The key has been removed from the group.')

    return redirect(reverse('servers.views.servers_show', args=(server.pk, )))


@login_required
@staff_member_required
def servers_groupsaccess_add(request, pk):
    """Add a server to allowed server into a group"""

    server = get_object_or_404(Server, pk=pk)

    group = get_object_or_404(Group, pk=request.GET.get('groupPk'))

    user_pk = request.GET.get('userPk')

    if user_pk == '0':
        group.allowed_servers.add(server)
        messages.success(request, 'The server has been added to the group (all users).')
    else:
        user = get_object_or_404(ServerUser, pk=user_pk, server=server)
        group.allowed_servers_users.add(user)
        messages.success(request, 'The server has been added to the group (' + user.name + ').')

    return redirect(reverse('servers.views.servers_show', args=(server.pk, )))


@login_required
@staff_member_required
def servers_groupsaccess_delete(request, pk, groupPk):
    """Delete a server form a group's allowed server"""

    server = get_object_or_404(Server, pk=pk)

    group = get_object_or_404(Group, pk=groupPk)

    group.allowed_servers.remove(server)

    messages.success(request, 'The server has been removed from the group.')

    return redirect(reverse('servers.views.servers_show', args=(server.pk, )))


@login_required
@staff_member_required
def servers_groupsaccess_user_delete(request, pk, groupPk, userPk):
    """Remove a user from a group's allowed user"""

    server = get_object_or_404(Server, pk=pk)

    user = get_object_or_404(ServerUser, pk=userPk)

    group = get_object_or_404(Group, pk=groupPk)

    group.allowed_servers_users.remove(user)

    messages.success(request, 'The user has been removed from the group.')

    return redirect(reverse('servers.views.servers_show', args=(server.pk, )))


@login_required
@staff_member_required
def servers_map(request):
    """Show a nice map of servers"""

    proxmox_servers = Server.objects.order_by('name').filter(is_proxmox=True).all()
    outside_servers = Server.objects.order_by('name').filter(is_proxmox=False, is_vm=False).all()

    return render_to_response('servers/map.html', {'proxmox_servers': proxmox_servers, 'outside_servers': outside_servers}, context_instance=RequestContext(request))
