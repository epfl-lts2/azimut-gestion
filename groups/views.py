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

from groups.models import Group
from groups.forms import GroupForm


@login_required
@staff_member_required
def groups_list(request):
    """Show the list of groups"""

    liste = Group.objects.order_by('name').all()

    return render_to_response('groups/groups/list.html', {'liste': liste}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def groups_show(request, pk):
    """Show details of an Group"""

    object = get_object_or_404(Group, pk=pk)

    return render_to_response('groups/groups/show.html', {'object': object}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def groups_edit(request, pk):
    """Edit an Group"""

    try:
        object = Group.objects.get(pk=pk)
    except:
        object = Group()

    if request.method == 'POST':  # If the form has been submitted...
        form = GroupForm(request.POST, instance=object)

        if form.is_valid():  # If the form is valid
            object = form.save()

            messages.success(request, 'The group has been saved.')

            return redirect(reverse('groups.views.groups_list'))
    else:
        form = GroupForm(instance=object)

    return render_to_response('groups/groups/edit.html', {'form': form}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def groups_delete(request, pk):
    """Delete a group"""

    object = get_object_or_404(Group, pk=pk)

    object.delete()

    messages.success(request, 'Group has been deleted.')

    return redirect(reverse('groups.views.groups_list', args=()))
