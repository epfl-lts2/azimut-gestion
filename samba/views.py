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

from samba.models import Share
from samba.forms import ShareForm
from servers.models import Server
from samba.tasks import update_samba


@login_required
@staff_member_required
def shares_list(request):
    """Show the list of hostname forwarded"""

    liste = Share.objects.order_by('name').all()

    return render_to_response('samba/shares/list.html', {'liste': liste}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def shares_show(request, pk):
    """Show details of a hostname forwarder"""

    object = get_object_or_404(Share, pk=pk)

    return render_to_response('samba/shares/show.html', {'object': object}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def shares_edit(request, pk):
    """Edit an Share"""

    try:
        object = Share.objects.get(pk=pk)
    except:
        object = Share()

    if request.method == 'POST':  # If the form has been submitted...
        form = ShareForm(request.POST, instance=object)

        if form.is_valid():  # If the form is valid
            object = form.save()

            messages.success(request, 'The share has been saved.')

            update_samba.delay()

            return redirect(reverse('samba.views.shares_list'))
    else:
        form = ShareForm(instance=object)

    return render_to_response('samba/shares/edit.html', {'form': form}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def shares_delete(request, pk):
    """Delete a Share"""

    object = get_object_or_404(Share, pk=pk)

    object.delete()

    messages.success(request, 'The share has been deleted.')

    update_samba.delay()

    return redirect(reverse('samba.views.shares_list', args=()))


def get_config(request, pk):
    """Return the config for a server"""

    server = get_object_or_404(Server, pk=pk)

    config = "# Samba configuration file for shares. Automaticaly generated !\n\n"

    for share in server.share_set.all():
        config += "[" + share.name + "]\n"
        config += "  path = " + share.get_full_path() + "\n"
        config += "  browseable = yes\n"
        config += "  guest ok = no\n"
        config += "  writeable = yes\n"
        config += "  valid users = " + share.get_username() + "\n\n\n"

    return HttpResponse(config)
