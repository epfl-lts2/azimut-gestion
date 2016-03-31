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

from hostnameforwarding.models import Hostnameforwarded
from hostnameforwarding.forms import HostnameforwardedForm
from servers.models import Server
from hostnameforwarding.tasks import update_hostnameforwarding


@login_required
@staff_member_required
def hosts_list(request):
    """Show the list of hostname forwarded"""

    liste = Hostnameforwarded.objects.order_by('domain').all()

    return render_to_response('hostnameforwarding/hosts/list.html', {'liste': liste}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def hosts_show(request, pk):
    """Show details of a hostname forwarder"""

    object = get_object_or_404(Hostnameforwarded, pk=pk)

    return render_to_response('hostnameforwarding/hosts/show.html', {'object': object}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def hosts_edit(request, pk):
    """Edit an Hostnameforwarded"""

    try:
        object = Hostnameforwarded.objects.get(pk=pk)
    except:
        object = Hostnameforwarded()

    if request.method == 'POST':  # If the form has been submitted...
        form = HostnameforwardedForm(request.POST, instance=object)

        if form.is_valid():  # If the form is valid
            object = form.save()

            messages.success(request, 'The port has been saved.')

            update_hostnameforwarding.delay()

            return redirect(reverse('hostnameforwarding.views.hosts_list'))
    else:
        form = HostnameforwardedForm(instance=object)

    return render_to_response('hostnameforwarding/hosts/edit.html', {'form': form}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def hosts_delete(request, pk):
    """Delete a Hostnameforwarded"""

    object = get_object_or_404(Hostnameforwarded, pk=pk)

    object.delete()

    messages.success(request, 'The port has been deleted.')

    update_hostnameforwarding.delay()

    return redirect(reverse('hostnameforwarding.views.hosts_list', args=()))


@login_required
@staff_member_required
def save_from_server(request, pk):
    """Save a hostnameforwarding entry from the server view"""

    server_from = get_object_or_404(Server, pk=request.POST.get('server_from'), is_vm=False)
    server_to = get_object_or_404(Server, pk=request.POST.get('server_to'), is_vm=True)

    try:

        port_to = int(request.POST.get('to'))
        port_from = int(request.POST.get('from'))
        domain = request.POST.get('domain')

        Hostnameforwarded(server_host=server_from, server_to=server_to, port_from=port_from, port_to=port_to, domain=domain).save()

        messages.success(request, 'The port has been saved.')

        update_hostnameforwarding.delay()

    except:
        pass

    return redirect(reverse('servers.views.servers_show', args=(pk,)))


@login_required
@staff_member_required
def delete_from_server(request, pk, portPk):
    """Delete a hostnameforwarding entry from the server view"""

    port = get_object_or_404(Hostnameforwarded, pk=portPk)

    port.delete()

    messages.success(request, 'The port has been deleted.')

    update_hostnameforwarding.delay()

    return redirect(reverse('servers.views.servers_show', args=(pk,)))


def get_conf(request, pk):
    """Build ngnix config for a server"""

    obj = get_object_or_404(Server, pk=pk)

    script = """# Automatic configuration
server {
    # Default server

    root /usr/share/nginx/www;
    index index.html index.htm;
"""

    if settings.NGNIX_DEFAULT_REDIRECT:
        script += """
    return 301 """ + settings.NGNIX_DEFAULT_REDIRECT + """;
"""

    script += """
    server_name localhost;

}
"""

    for host in obj.hoststoforward.filter(base_path='/').all():
        script += """server {
    listen """ + str(host.port_from) + """;
    server_name """ + host.domain + """;
    client_max_body_size 101M;

    """

        if not host.force_https:

            for sub_host in obj.hoststoforward.filter(domain=host.domain, port_from=host.port_from):

                script += """location """ + sub_host.base_path + """ {
                """

                if sub_host.base_path != '/' and sub_host.dest_path != '/':
                    script += """        rewrite ^/""" + sub_host.base_path[:-1] + """(/.*)$ $1 break;
            """

                if sub_host.port_to == 80:
                    script += """        proxy_pass http://""" + sub_host.server_to.internal_ip + sub_host.dest_path + """;
            """
                else:
                    script += """        proxy_pass http://""" + sub_host.server_to.internal_ip + """:""" + str(sub_host.port_to) + sub_host.dest_path + """;
            """

                if sub_host.port_from == 443 and settings.NGNIX_SSL_PEM != '' and settings.NGNIX_SSL_KEY != '':
                    script += """        proxy_redirect          http:// https://;
            """

                script += """        access_log off;
            proxy_set_header        X-Real-IP       $remote_addr;
            proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header        Host            $host;
            proxy_set_header        X-Forwarded-Proto $scheme;

            }
            """

        if host.port_from == 443 and settings.NGNIX_SSL_PEM != '' and settings.NGNIX_SSL_KEY != '':
            script += """        ssl on;
    """
            script += """        ssl_certificate      """ + (host.custom_https_certificate_pem or settings.NGNIX_SSL_PEM) + """;
    """
            script += """        ssl_certificate_key  """ + (host.custom_https_certificate_key or settings.NGNIX_SSL_KEY) + """;
    """

        if host.force_https:
                script += """      return 301 https://$server_name$request_uri;
            """

        script += """
    }
        """

    return HttpResponse(script)
