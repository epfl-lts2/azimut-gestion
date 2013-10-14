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

from pyproxmox import *

from servers.models import Server

from operator import itemgetter

from proxmoxs.forms import NewVMForm, EditVMFOrm


def gimme_prox_cox(server):
    """Return a proxmox connection"""

    return pyproxmox(prox_auth(server, settings.PROXMOX_USER, settings.PROXMOX_PASS))


@login_required
@staff_member_required
def vms_list(request):
    """Show the list of VMs"""

    liste = []

    for server in Server.objects.filter(is_proxmox=True).exclude(proxmox_node_name='').all():
        retour = gimme_prox_cox(server.ip_for_proxmox()).getNodeContainerIndex(server.proxmox_node_name)

        vm_list = []
        vm_servers_linked = []
        servers_unlinked = []

        if 'data' in retour:
            vm_list = []

            for elem in retour['data']:

                def cal_color(val):
                    """Return the color to use for a precent"""

                    if val > 85:
                        return 'danger'
                    if val > 60:
                        return 'warning'
                    return 'success'

                elem['cpu_percent'] = 100.0 * elem['cpu'] / elem['cpus']
                elem['mem_percent'] = 100.0 * elem['mem'] / elem['maxmem']
                elem['disk_percent'] = 100.0 * elem['disk'] / elem['maxdisk']

                if elem['maxswap']:
                    elem['swap_percent'] = 100.0 * elem['swap'] / elem['maxswap']
                else:
                    elem['swap_percent'] = 0

                elem['cpu_percent_color'] = cal_color(elem['cpu_percent'])
                elem['mem_percent_color'] = cal_color(elem['mem_percent'])
                elem['disk_percent_color'] = cal_color(elem['disk_percent'])
                elem['swap_percent_color'] = cal_color(elem['swap_percent'])

                m, s = divmod(int(elem['uptime']), 60)
                h, m = divmod(m, 60)
                d, h = divmod(h, 24)

                elem['uptime_s'] = s
                elem['uptime_m'] = m
                elem['uptime_h'] = h
                elem['uptime_d'] = d

                try:
                    elem['server'] = server.server_set.filter(internal_ip=elem['ip']).all()[0]
                    vm_servers_linked.append(elem['server'].pk)
                except IndexError:
                    elem['server'] = None

                vm_list.append(elem)

            vm_list = sorted(vm_list, key=itemgetter('name'))

        for server_unlinked in server.server_set.exclude(pk__in=vm_servers_linked).exclude(internal_ip=None).all():
            servers_unlinked.append(server_unlinked)

        liste.append((server, vm_list, servers_unlinked))

    return render_to_response('proxmoxs/vms/list.html', {'liste': liste}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def vms_stop(request, serverPk, vmId):
    """Stop a vm"""

    object = get_object_or_404(Server, pk=serverPk)

    if request.method == 'POST' and request.POST.get('iam', '') == 'sure':

        if gimme_prox_cox(object.ip_for_proxmox()).stopOpenvzContainer(object.proxmox_node_name, vmId):
            messages.success(request, 'VM has been stopped.')
        else:
            messages.warning(request, 'Cannot stop the VM.')

        return redirect(reverse('proxmoxs.views.vms_list', args=()))

    else:
        return render_to_response('confirm.html', {'title': 'Stopping a VM', 'message': 'The VM with ID ' + str(vmId) + ' of server ' + str(object) + ' will be stopped !'}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def vms_start(request, serverPk, vmId):
    """Start a vm"""

    object = get_object_or_404(Server, pk=serverPk)

    if gimme_prox_cox(object.ip_for_proxmox()).startOpenvzContainer(object.proxmox_node_name, vmId):
        messages.success(request, 'VM has been started.')
    else:
        messages.warning(request, 'Cannot start the VM.')

    return redirect(reverse('proxmoxs.views.vms_list', args=()))


@login_required
@staff_member_required
def vms_delete(request, serverPk, vmId):
    """Delete a vm"""

    object = get_object_or_404(Server, pk=serverPk)

    if request.method == 'POST' and request.POST.get('iam', '') == 'sure':

        if gimme_prox_cox(object.ip_for_proxmox()).deleteOpenvzContainer(object.proxmox_node_name, vmId):
            messages.success(request, 'VM has been deleted.')
        else:
            messages.warning(request, 'Cannot delete the VM.')

        return redirect(reverse('proxmoxs.views.vms_list', args=()))

    else:

        return render_to_response('confirm.html', {'title': 'Deleting a VM', 'message': 'The VM with ID ' + str(vmId) + ' of server ' + str(object) + ' will be DELETED !'}, context_instance=RequestContext(request))


def check_if_ip_exists(com, server, ip):
    """Check if an ip exists on the server"""

    for vm in com.getNodeContainerIndex(server.proxmox_node_name)['data']:
        if vm['ip'] == ip:
            return False

    return True


def get_templates(com, server):
    """Return a list of tempaltes"""
    storages = com.getNodeStorage(server.proxmox_node_name)['data']

    templates = []

    for storage_data in storages:
        for storage_content in com.getNodeStorageContent(server.proxmox_node_name, storage_data['storage'])['data']:
            if storage_content['content'] == 'vztmpl':
                templates.append((storage_content['volid'], storage_content['volid'].split('/')[-1]))

    return templates


@login_required
@staff_member_required
def vms_create(request, serverPk):
    """Create a new VM"""

    object = get_object_or_404(Server, pk=serverPk)

    if not object.internal_ip or object.internal_ip == '':
        messages.error(request, 'No internal ip')
        return redirect(reverse('proxmoxs.views.vms_list', args=()))

    com = gimme_prox_cox(object.vm_host.ip_for_proxmox())

    templates = get_templates(com, object.vm_host)

    if request.method == 'POST':  # If the form has been submitted...
        form = NewVMForm(templates, request.POST)

        if form.is_valid():  # If the form is valid

            if not check_if_ip_exists(com, object.vm_host, object.internal_ip):
                messages.error(request, 'Server with IP already exist')
            else:

                id = com.getClusterVmNextId()['data']

                post_data = {'ostemplate': form.cleaned_data['template'], 'vmid': id, 'cpus': form.cleaned_data['cpus'], 'description': 'fabric-manual',
                             'disk': form.cleaned_data['disk'], 'hostname': object.name, 'memory': form.cleaned_data['ram'],
                             'password': object.random_proxmox_password(), 'swap': form.cleaned_data['swap'], 'ip_address': object.internal_ip}

                com.createOpenvzContainer(object.vm_host.proxmox_node_name, post_data)

                messages.success(request, 'The VM has been created.')

                return redirect(reverse('proxmoxs.views.vms_list', args=()))
    else:
        form = NewVMForm(templates)

    return render_to_response('proxmoxs/vms/create.html', {'form': form, 'object': object}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def vms_update(request, serverPk, vmId):
    """Update settings for a virutal machine"""

    object = get_object_or_404(Server, pk=serverPk)

    com = gimme_prox_cox(object.ip_for_proxmox())

    infos = com.getContainerStatus(object.proxmox_node_name, vmId)

    if not infos or 'data' not in infos:
        raise Http404

    disk = infos['data']['maxdisk'] / (1024 * 1024 * 1024)
    mem = infos['data']['maxmem'] / (1024 * 1024)
    swap = infos['data']['maxswap'] / (1024 * 1024)
    cpus = infos['data']['cpus']

    if request.method == 'POST':

        form = EditVMFOrm(disk, mem, swap, cpus, request.POST)

        if form.is_valid():

            post_data = {'cpus': form.cleaned_data['cpus'], 'disk': form.cleaned_data['disk'], 'swap': form.cleaned_data['swap'], 'memory': form.cleaned_data['ram']}

            com.setOpenvzContainerOptions(object.proxmox_node_name, vmId, post_data)

            messages.success(request, 'The VM has been updated.')

            return redirect(reverse('proxmoxs.views.vms_list', args=()))

    else:

        form = EditVMFOrm(disk, mem, swap, cpus)

    return render_to_response('proxmoxs/vms/update.html', {'form': form, 'object': object}, context_instance=RequestContext(request))
