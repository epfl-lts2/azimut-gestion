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

from backups.models import Backup, BackupRun, BackupSetOfRun, BackupNotification, BackupUserWhoWantNotifs
from backups.forms import BackupForm
from backups.tasks import run_backup

from django.contrib.auth.models import User

from django.utils import timezone
import datetime
import json


@login_required
@staff_member_required
def backups_list(request):
    """Show the list of backups"""

    liste = Backup.objects.order_by('name').all()

    return render_to_response('backups/backups/list.html', {'liste': liste}, context_instance=RequestContext(request))


@login_required
def backups_show(request, pk):
    """Show details of a backup"""

    object = get_object_or_404(Backup, pk=pk)

    if not request.user.is_staff and (request.user not in object.server_from.users_owning_the_server.all() and request.user not in object.server_to.users_owning_the_server.all()):
        raise Http404

    liste = object.backuprun_set.order_by('-start_date').all()

    return render_to_response('backups/backups/show.html', {'object': object, 'liste': liste}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def backups_edit(request, pk):
    """Edit a backup"""

    try:
        object = Backup.objects.get(pk=pk)
    except:
        object = Backup()

    if request.method == 'POST':  # If the form has been submitted...
        form = BackupForm(request.POST, instance=object)

        if form.is_valid():  # If the form is valid
            object = form.save()

            messages.success(request, 'The backup has been saved.')

            return redirect(reverse('backups.views.backups_list'))
    else:
        form = BackupForm(instance=object)

    return render_to_response('backups/backups/edit.html', {'form': form}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def backups_delete(request, pk):
    """Delete a backup"""

    object = get_object_or_404(Backup, pk=pk)

    object.delete()

    messages.success(request, 'The backup has been deleted. The destination folder has not been removed !')

    return redirect(reverse('backups.views.backups_list', args=()))


@login_required
@staff_member_required
def backups_run(request, pk):
    """Run a backup"""

    object = get_object_or_404(Backup, pk=pk)

    run_backup.delay(object.pk)

    messages.success(request, 'The backup is running')

    return redirect(reverse('backups.views.backups_list', args=()))


def get_conf(request, pk):
    """Build rsnapshot config for a backup"""

    backup = get_object_or_404(Backup, pk=pk)

    excludes = ''

    if backup.prox_and_sys_excludes:
        excludes += ' --exclude=/proc --exclude=/sys'

    if backup.excludes:
        for folder in backup.excludes.split(','):
            excludes += ' --exclude=' + folder

    cox_string = backup.server_from.ssh_connection_string_from_backup.split(' ')

    ssh_args = '-p 22'

    if '-p' in cox_string:

        next_is_port = False
        for x in cox_string:
            if next_is_port:
                next_is_port = False
                ssh_args = '-p ' + x

            if x == '-p':
                next_is_port = True

        cox = cox_string[-1]
    else:
        cox = cox_string[-1]

    script = """config_version\t1.2

snapshot_root\t""" + backup.folder_to + """

cmd_rsync\t/usr/bin/rsync
cmd_ssh\t/usr/bin/ssh
cmd_rm\t/bin/rm
cmd_logger\t/usr/bin/logger
cmd_du\t/usr/bin/du

retain\thourly\t6
retain\tdaily\t7
retain\tweekly\t7
retain\tmonthly\t3

link_dest\t1
cmd_cp\t/bin/cp

use_lazy_deletes\t1

ssh_args\t""" + ssh_args + """
rsync_long_args\t--delete --numeric-ids --relative --delete-excluded --stats""" + excludes + """

backup\t""" + cox + ':' + backup.folder_from + """\t.
"""

    return HttpResponse(script)


@login_required
@staff_member_required
def clean_up(request):

    for b in BackupRun.objects.filter(start_date__lt=timezone.now() - datetime.timedelta(days=1)).all():
        if b.backupsetofrun_set.count() == 0:
            b.delete()

    messages.success(request, "Old backups runs have been deleted")

    return HttpResponseRedirect(reverse('backups.views.backups_list'))


@login_required
@staff_member_required
def backupsets_list(request):
    """Show the list of backup sets"""

    liste = BackupSetOfRun.objects.order_by('-start_date').all()

    return render_to_response('backups/backupsets/list.html', {'liste': liste}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def backupsets_cancel(request, pk):

    backupset = get_object_or_404(BackupSetOfRun, pk=pk, status='running')
    backupset.status = 'canceled'
    backupset.end_date = timezone.now()
    backupset.save()

    bn = BackupNotification(type='bkpsetcanceled')
    bn.message = "The backupset of type %s, started at %s, has been set as canceled." % (backupset.type, str(backupset.start_date), )
    bn.save()
    bn.send_notifications()

    return HttpResponseRedirect(reverse('backups.views.backupsets_list'))


@login_required
@staff_member_required
def clean_up_old_sets(request):

    NB_OK = {'hourly': 6, 'daily': 7, 'weekly': 7, 'monthly': 3}

    for b in BackupSetOfRun.objects.order_by('-start_date').all():
        if NB_OK[b.type] >= 0:
            NB_OK[b.type] -= 1
        else:
            b.delete()

    messages.success(request, "Old backups sets have been deleted")

    return HttpResponseRedirect(reverse('backups.views.backupsets_list'))


@login_required
@staff_member_required
def backupnotifications_list(request):
    """Show the list of backup notifications"""

    liste = BackupNotification.objects.order_by('-when').all()

    notif_types = BackupNotification.get_types_with_labels()

    users_with_things = []

    for u in User.objects.order_by('username').all():
        data = []

        for key, __, __ in notif_types:
            data.append((key, BackupUserWhoWantNotifs.objects.filter(type=key, user=u).count() > 0))

        users_with_things.append((u, data))

    return render_to_response('backups/backupnotifications/list.html', {'liste': liste, 'notif_types': notif_types, 'users_with_things': users_with_things}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def backupnotifications_switch(request):
    """Switch a backup notification"""

    (obj, created) = BackupUserWhoWantNotifs.objects.get_or_create(type=request.GET.get('key'), user=get_object_or_404(User, pk=request.GET.get('uPk')))

    if not created:
        obj.delete()

    return render_to_response('backups/backupnotifications/switch.html', {'is_ok': created}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def clean_up_notifications(request):

    for b in BackupNotification.objects.filter(when__lt=timezone.now() - datetime.timedelta(days=15)).all():
        b.delete()

    messages.success(request, "Old notifications have been deleted")

    return HttpResponseRedirect(reverse('backups.views.backupnotifications_list'))


def zabbix_list(request):

    data = []

    for b in Backup.objects.filter(active=True).all():
        data.append({'{#BACKUP_ID}': b.pk, '{#BACKUP_NAME}': b.name})

    # return HttpResponse(build_zabbix_json(data))
    return HttpResponse(json.dumps({'data': data}))


def zabbix_last_nb_hours(request, pk, mode):

    backup = get_object_or_404(Backup, pk=pk)

    elem = backup.backuprun_set.order_by('-start_date').exclude(end_date=None).filter(type=mode)

    if elem.count() == 0:
        return HttpResponse('0')

    last_elem = elem.all()[0]

    diff = (timezone.now() - last_elem.start_date).total_seconds() / 3600.0

    diff = int(diff)

    if diff == 0:
        diff = 1

    return HttpResponse(str(diff))


def zabbix_last_files_or_size(request, pk, mode):


    backup = get_object_or_404(Backup, pk=pk)

    elem = backup.backuprun_set.order_by('-start_date').exclude(end_date=None).filter(type='hourly')

    if elem.count() == 0:
        return HttpResponse('0')

    last_elem = elem.all()[0]

    val = last_elem.size if mode == 'size' else last_elem.nb_files

    return HttpResponse(str(val))


def zabbix_last_hourly_duration(request):

    bs = BackupSetOfRun.objects.filter(type='hourly', status='done').exclude(total_size=0).order_by('-start_date')

    if bs.count():
        return HttpResponse(str(bs.get_total_time()))

    return HttpResponse("0")
