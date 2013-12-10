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

import subprocess

from django.utils import timezone

from servers.models import Server
from fabrun.models import Task
from fabrun.tasks import run_task

import datetime

KEYWORDS = ('[$AG:NeedGestion]', '[$AG:NeedKM]', '[$AG:NeedUser]')


@login_required
@staff_member_required
def home(request):
    """Show the page to execute scripts"""

    if request.method == 'POST':

        task = request.POST.get('script')

        if task:
            for spk in request.POST.getlist('server'):

                server = get_object_or_404(Server, pk=spk)

                t = Task(creation_date=timezone.now(), server=server, command=task)
                t.save()
                run_task.delay(t.pk)

                messages.success(request, "Created task for server " + str(server))

    liste = []

    out, __ = subprocess.Popen(['fab', '--shortlist'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=settings.FABRIC_FOLDER).communicate()

    # for command in out.split('\n'):

    #     if command:

    #         out2, __ = subprocess.Popen(['fab', '-d', command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=settings.FABRIC_FOLDER).communicate()

    #         description = out2.split('\n')[2]

    #         for keyword in KEYWORDS:
    #             description = description.replace(keyword, '')

    #         description = description.strip()

    #         liste.append((command, description))

    liste = out.split('\n')

    servers = Server.objects.exclude(ssh_connection_string_from_gestion=None).order_by('name').all()

    tasks = Task.objects.order_by('-creation_date').all()

    return render_to_response('fabrun/home.html', {'liste': liste, 'tasks': tasks, 'servers': servers}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def show_run(request, pk):
    """Show output for a run"""

    task = get_object_or_404(Task, pk=pk)

    return render_to_response('fabrun/show_run.html', {'task': task}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def clean_up(request):

    Task.objects.filter(creation_date__lt = timezone.now() - datetime.timedelta(days=1)).delete()

    messages.success(request, "Old fabric runs have been deleted")

    return HttpResponseRedirect(reverse('fabrun.views.home'))


@login_required
@staff_member_required
def get_description(request):

    command = request.GET.get('task')

    out, __ = subprocess.Popen(['fab', '--shortlist'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=settings.FABRIC_FOLDER).communicate()

    if command in out.split('\n'):

        out2, __ = subprocess.Popen(['fab', '-d', command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=settings.FABRIC_FOLDER).communicate()

        description = out2.split('\n')[2]

        for keyword in KEYWORDS:
            description = description.replace(keyword, '')

        description = description.strip()

        return HttpResponse(description)

    raise Http404
