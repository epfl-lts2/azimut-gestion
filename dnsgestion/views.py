
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

from dnsgestion.models import Zone, Entry
from dnsgestion.forms import ZoneForm, EntryForm
from servers.models import Server

import time

from dnsgestion.tasks import update_dns


@login_required
@staff_member_required
def zones_list(request):
    """Show the list of zones"""

    liste = Zone.objects.order_by('name').all()

    return render_to_response('dnsgestion/zones/list.html', {'liste': liste}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def zones_show(request, pk):
    """Show details of an Zone"""

    object = get_object_or_404(Zone, pk=pk)

    return render_to_response('dnsgestion/zones/show.html', {'object': object}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def zones_edit(request, pk):
    """Edit an Zone"""

    try:
        object = Zone.objects.get(pk=pk)
    except:
        object = Zone()

    if request.method == 'POST':  # If the form has been submitted...
        form = ZoneForm(request.POST, instance=object)

        if form.is_valid():  # If the form is valid
            object = form.save()

            messages.success(request, 'The zone has been saved.')

            return redirect(reverse('dnsgestion.views.zones_list'))
    else:
        form = ZoneForm(instance=object)

    return render_to_response('dnsgestion/zones/edit.html', {'form': form}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def zones_delete(request, pk):
    """Delete a zone"""

    object = get_object_or_404(Zone, pk=pk)

    object.delete()

    messages.success(request, 'Zone has been deleted.')

    return redirect(reverse('dnsgestion.views.zones_list', args=()))


@login_required
@staff_member_required
def entry_edit(request, pk):
    """Edit an entry"""

    try:
        object = Entry.objects.get(pk=pk)
    except:
        object = Entry()

        object.zone = get_object_or_404(Zone, pk=request.GET.get('zone'))
        object.order = 900000

    if request.method == 'POST':  # If the form has been submitted...
        form = EntryForm(request.POST, instance=object)

        if form.is_valid():  # If the form is valid
            object = form.save()

            messages.success(request, 'The zone has been saved.')

            object.zone.reorder()

            return redirect(reverse('dnsgestion.views.zones_show', args=(object.zone.pk,)))
    else:
        form = EntryForm(instance=object)

    return render_to_response('dnsgestion/entries/edit.html', {'form': form}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def entry_delete(request, pk):
    """Delete an entry"""

    object = get_object_or_404(Entry, pk=pk)

    pk = object.zone.pk

    object.delete()

    messages.success(request, 'Entry has been deleted.')

    return redirect(reverse('dnsgestion.views.zones_show', args=(pk,)))


@login_required
@staff_member_required
def entry_up(request, pk):
    """Move an entry up"""

    object = get_object_or_404(Entry, pk=pk)

    old_id = 0
    old_elem = None

    for e in object.zone.entries():
        if e.pk == object.pk and old_elem:
            old_elem.order = e.order
            old_elem.save()
            e.order = old_id
            e.save()
        old_elem = e

    object.zone.reorder()

    return redirect(reverse('dnsgestion.views.zones_show', args=(object.zone.pk,)))


@login_required
@staff_member_required
def entry_down(request, pk):
    """Move an entry down"""

    object = get_object_or_404(Entry, pk=pk)

    old_id = 0
    old_elem = None

    for e in object.zone.entries():
        if old_elem:
            old_id = old_elem.order
            old_elem.order = e.order
            e.order = old_id

            old_elem.save()
            e.save()

            old_elem = None

        if e.pk == object.pk:
            old_elem = e

    object.zone.reorder()

    return redirect(reverse('dnsgestion.views.zones_show', args=(object.zone.pk,)))


@login_required
@staff_member_required
def zones_deploy(request, pk):
    """Deploy a zone"""

    object = get_object_or_404(Zone, pk=pk)

    update_dns.delay(object.server.pk)

    messages.success(request, 'Zone has been scheduled for deploy.')

    return redirect(reverse('dnsgestion.views.zones_show', args=(object.pk,)))


@login_required
@staff_member_required
def zones_increment_and_deploy(request, pk):
    """Increment and deploy a zone"""

    object = get_object_or_404(Zone, pk=pk)

    base_id = int(time.strftime("%Y%m%d00"))

    while base_id <= object.serial:
        base_id += 1

    object.serial = base_id
    object.save()

    update_dns.delay(object.server.pk)

    messages.success(request, 'Zone has been scheduled for deploy.')

    return redirect(reverse('dnsgestion.views.zones_show', args=(object.pk,)))


def generate_main_file(request, pk, secret):
    """Generate main bind file"""

    if secret != settings.DNS_SECRET:
        raise Http404()

    object = get_object_or_404(Server, pk=pk)

    output = """//
// Azimut-gestion generated files. Don't edit !
//
"""

    for zone in object.zone_set.all():
        output += """zone "%s" {
    type master;
    file "/etc/bind/db.generated.%s";
};
""" % (zone.name, zone.name, )

    return HttpResponse(output)


def generate_zone_file(request, pk, secret):
    """Generate main bind file"""

    if secret != settings.DNS_SECRET:
        raise Http404()

    object = get_object_or_404(Zone, pk=pk)

    output = """;
; Azimut-gestion generated files. Don't edit !
;

$TTL %s

%s. IN SOA %s %s (
    %s  \t; Serial
    %s  \t\t\t; Refresh
    %s  \t\t\t; Retry
    %s  \t\t; Expire
    %s )\t\t\t; Negative TTL Cache

""" % (object.default_ttl, object.name, object.name_server, object.contact_email.replace('@', '.'),
       object.serial, object.refresh, object.retry, object.expiry, object.negative_ttl)

    for entry in object.entries().filter(disabled=False):
        output += """%s\t\t\t%s\t\t%s\t\t\t%s
""" % (entry.label, entry.entry_class, entry.entry_type, entry.value)

    return HttpResponse(output)
