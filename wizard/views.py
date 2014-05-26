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

from uuid import uuid4

from wizards import wizs

from wizard.models import Execution
from wizard.tasks import do_task_step


@login_required
@staff_member_required
def home(request):
    """Show the list of wizards"""

    liste = []

    for elem in wizs:
        wiz = wizs[elem]([], [])
        liste.append((wiz.get_name(), wiz.get_description(), elem))

    if request.method == 'POST':

        task = request.POST['script']

        uid = str(uuid4())

        if task not in wizs:
            messages.warning(request, "Unknow task ?")

        else:

            request.session['wiz_' + uid + '_class'] = task
            request.session['wiz_' + uid + '_cstep'] = 1
            request.session['wiz_' + uid + '_ctask'] = False

            request.session['wiz_' + uid + '_status_id'] = -1

            return HttpResponseRedirect(reverse('wizard.views.do_step', args=(uid,)))

    return render_to_response('wizard/home.html', {'liste': liste}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def do_step(request, uid):
    """Execute a step of a wizard"""

    task = request.session.get('wiz_' + uid + '_class')

    if not task:
        raise Http404
        return

    if task not in wizs:
        raise Http404
        return

    if request.session['wiz_' + uid + '_ctask']:
        raise Http404
        return

    step_data = []

    step = request.session['wiz_' + uid + '_cstep']

    for i in range(1, step):
        step_data.append(request.session['wiz_' + uid + '_step_data' + str(i)])

    wiz = wizs[task](step_data, [])

    (text, form, js) = getattr(wiz, 'display_step_' + str(step))(request)

    if request.method == 'POST' and form.is_valid():

        request.session['wiz_' + uid + '_step_data' + str(step)] = getattr(wiz, 'save_step_' + str(step))(form)

        request.session['wiz_' + uid + '_cstep'] += 1

        if request.session['wiz_' + uid + '_cstep'] > wiz.get_nb_step():
            request.session['wiz_' + uid + '_ctask'] = True
            return HttpResponseRedirect(reverse('wizard.views.do_tasks', args=(uid,)))
        else:
            return HttpResponseRedirect(reverse('wizard.views.do_step', args=(uid,)))

    return render_to_response('wizard/step.html', {'wiz': wiz, 'form': form, 'text': text, 'js': js, 'step': step, 'steps': wiz.get_steps_name()[:step]}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def do_tasks(request, uid):
    """Execute tasks of a wizard"""

    task = request.session.get('wiz_' + uid + '_class')

    if not task:
        raise Http404
        return

    if task not in wizs:
        raise Http404
        return

    if not request.session['wiz_' + uid + '_ctask']:
        raise Http404
        return

    step_data = []

    step = request.session['wiz_' + uid + '_cstep']

    for i in range(1, step):
        step_data.append(request.session['wiz_' + uid + '_step_data' + str(i)])

    wiz = wizs[task](step_data, [])

    tasks = wiz.get_tasks_name()

    if request.session['wiz_' + uid + '_status_id'] == -1:

        ex = Execution(current_task=0, done=False)
        ex.save()

        request.session['wiz_' + uid + '_status_id'] = ex.pk

        do_task_step.delay(task, ex.pk, 1, step_data, [])

    status_id = request.session['wiz_' + uid + '_status_id']

    return render_to_response('wizard/task.html', {'wiz': wiz, 'tasks': tasks, 'nb_tasks': wiz.get_nb_task(), 'status_id': status_id}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def get_task_status(request, pk):
    """Return the task status of a wizard"""

    ex = get_object_or_404(Execution, pk=pk)

    return HttpResponse(str(ex.current_task) + ',' + str(ex.done))
