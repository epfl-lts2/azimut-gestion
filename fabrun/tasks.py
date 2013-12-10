from celery import task

from fabrun.models import Task
from django.utils import timezone
import subprocess
from django.conf import settings


@task(ignore_result=True)
def run_task(id):
    """Run a task"""

    task = Task.objects.get(pk=id)
    task.start_date = timezone.now()
    task.save()

    out2, __ = subprocess.Popen(['fab', '-d', task.command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=settings.FABRIC_FOLDER).communicate()
    try:
        description = out2.split('\n')[2]
    except:
        task.stderr = 'Cannot get the command description'
        task.end_date = timezone.now()
        task.save()
        return

    if '[$AG:NeedGestion]' in description:
        needGestion = True
    else:
        needGestion = False

    if '[$AG:NeedKM]' in description:
        needKm = True
    else:
        needKm = False

    if '[$AG:NeedUser]' in description:
        needUser = True
    else:
        needUser = False

    if not task.server.ssh_connection_string_from_gestion:
        task.stderr = 'I don\'t know how to connect to the server'
        task.end_date = timezone.now()
        task.save()
        return

    if needKm and not task.server.keymanger_name:
        task.stderr = 'I need a keymanager name to execute this script.'
        task.end_date = timezone.now()
        task.save()
        return

    if needUser and not task.args:
        task.stderr = 'I need a user to execute this script (to put in args).'
        task.end_date = timezone.now()
        task.save()
        return

    thing_to_set = ''

    if needGestion:
        if task.server.vm_host.keymanger_name == settings.GESTION_VM_NAME:
            thing_to_set += ',gestion_ip=' + settings.GESTION_IP
            thing_to_set += ',gestion_name=' + settings.GESTION_NAME

    if needKm:
        thing_to_set += ',keymanagerName=' + task.server.keymanger_name
        thing_to_set += ',keyManagerUsers=' + task.server.get_users_list().replace(',', ' ')

    if needUser:
        thing_to_set += ',fab_user=' + task.args

    thing_to_set = thing_to_set[1:]

    out, err = subprocess.Popen(['fab', '--abort-on-prompts', '-p', task.server.random_proxmox_password(), '-H', task.server.get_host_for_fabric(), '--set=' + thing_to_set, task.command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=settings.FABRIC_FOLDER).communicate()

    task.stdout = out
    task.stderr = err

    task.end_date = timezone.now()
    task.save()
