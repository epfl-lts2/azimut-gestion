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

from portforwarding.models import Portforwarded
from portforwarding.forms import PortforwardedForm
from servers.models import Server
from portforwarding.tasks import update_portforwarding


@login_required
@staff_member_required
def ports_list(request):
    """Show the list of portforwarding"""

    liste = Portforwarded.objects.order_by('server_host__name', 'port_from').all()

    return render_to_response('portforwarding/ports/list.html', {'liste': liste}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def ports_show(request, pk):
    """Show details of aa portforwarded"""

    object = get_object_or_404(Portforwarded, pk=pk)

    return render_to_response('portforwarding/ports/show.html', {'object': object}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def ports_edit(request, pk):
    """Edit an Portforwarded"""

    try:
        object = Portforwarded.objects.get(pk=pk)
    except:
        object = Portforwarded()

    if request.method == 'POST':  # If the form has been submitted...
        form = PortforwardedForm(request.POST, instance=object)

        if form.is_valid():  # If the form is valid
            object = form.save()

            messages.success(request, 'The port has been saved.')

            update_portforwarding.delay()

            return redirect(reverse('portforwarding.views.ports_list'))
    else:
        form = PortforwardedForm(instance=object)

    return render_to_response('portforwarding/ports/edit.html', {'form': form}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def ports_delete(request, pk):
    """Delete a Portforwarded"""

    object = get_object_or_404(Portforwarded, pk=pk)

    object.delete()

    messages.success(request, 'The port has been deleted.')

    update_portforwarding.delay()

    return redirect(reverse('portforwarding.views.ports_list', args=()))


@login_required
@staff_member_required
def save_from_server(request, pk):
    """Save a portforwarding entry from the server view"""

    server_from = get_object_or_404(Server, pk=request.POST.get('server_from'), is_vm=False)
    server_to = get_object_or_404(Server, pk=request.POST.get('server_to'), is_vm=True)

    try:

        port_to = int(request.POST.get('to'))
        port_from = int(request.POST.get('from'))
        protocol = request.POST.get('protocol')

        Portforwarded(server_host=server_from, server_to=server_to, port_from=port_from, port_to=port_to, protocol=protocol).save()

        messages.success(request, 'The port has been saved.')

        update_portforwarding.delay()

    except:
        pass

    return redirect(reverse('servers.views.servers_show', args=(pk,)))


@login_required
@staff_member_required
def delete_from_server(request, pk, portPk):
    """Delete a portforwarding entry from the server view"""

    port = get_object_or_404(Portforwarded, pk=portPk)

    port.delete()

    messages.success(request, 'The port has been deleted.')

    update_portforwarding.delay()

    return redirect(reverse('servers.views.servers_show', args=(pk,)))


def get_script(request, pk):
    """Return the script for ipable generation"""

    obj = get_object_or_404(Server, pk=pk)

    if not obj.external_ip:
        raise Http404('No external ip')

    if not obj.external_interface:
        raise Http404("No external interface")

    script = """#!/bin/sh

case "$1" in
start) echo "Starting iptables NAT for openvz"
    /sbin/iptables -t nat -D POSTROUTING -s """ + settings.PROXMOX_IP_BASE + """.0/24 -o """ + obj.external_interface + """ -j SNAT --to """ + obj.external_ip + """
    /sbin/iptables -t nat -A POSTROUTING -s """ + settings.PROXMOX_IP_BASE + """.0/24 -o """ + obj.external_interface + """ -j SNAT --to """ + obj.external_ip + """
"""
    for pf in obj.portstoforward.all():
        script += """    /sbin/iptables -t nat -A PREROUTING -i """ + obj.external_interface + """ -p """ + pf.protocol + """ --dport """ + str(pf.port_from) + """ -j DNAT --to """ + pf.server_to.internal_ip + """:""" + str(pf.port_to) + """
        """

    script += """
    ;;
stop) echo "Stopping iptables NAT for openvz"
    /sbin/iptables -t nat -D POSTROUTING -s """ + settings.PROXMOX_IP_BASE + """.0/24 -o """ + obj.external_interface + """ -j SNAT --to """ + obj.external_ip + """
    /sbin/iptables -t nat --flush PREROUTING

    ;;
flush) echo "Flusing iptables NAT for openvz"
    /sbin/iptables -t nat --flush PREROUTING

    ;;
*) echo "Usage: /etc/init.d/nat-vz {start|stop|flush}"
    exit 2
    ;;
esac
exit 0
"""

    return HttpResponse(script)
