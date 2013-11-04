from celery import task

import re
from django.utils import timezone

from backups.models import Backup, BackupRun

import os
from django.conf import settings


@task(ignore_result=True)
def run_backup(id, mode='hourly'):
    """Run a backup"""

    backup = Backup.objects.get(pk=id)

    # Create the run
    backuprun = BackupRun(backup=backup, start_date=timezone.now())
    backuprun.save()

    # Backup
    if not backup.server_to.ssh_connection_string_from_gestion:
        print "Error: No connection from gestion"
        return

    if not backup.server_from.ssh_connection_string_from_backup:
        print "Error: No connection from backup"
        return

    os.system('ssh ' + backup.server_to.ssh_connection_string_from_gestion + ' wget ' + settings.GESTION_URL + 'backups/get_conf/' + str(backup.pk) + '/ -O /tmp/azimut-gestion-backup-config-' + str(backup.pk))

    to_do_string = ['rsnapshot -c /tmp/azimut-gestion-backup-config-' + str(backup.pk) + ' -v ' + mode]

    import subprocess
    p = subprocess.Popen(['ssh'] + backup.server_to.ssh_connection_string_from_gestion.split(' ') + [' '.join(to_do_string)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out, err = p.communicate()

    backuprun.end_date = timezone.now()
    backuprun.stdout = out
    backuprun.stderr = err

    try:
        backuprun.nb_files = re.search('Number of files: (\d*)', out).group(1) or 0
    except:
        print "Error getting nb files"
        pass
    try:
        backuprun.size = re.search('Total file size: (\d*)', out).group(1) or 0
    except:
        print "Error getting total file size"
        pass

    backuprun.save()


@task(ignore_result=True)
def run_active_backups(mode):
    """Run all actives backups"""

    for bkp in Backup.objects.filter(active=True).all():
        run_backup.delay(bkp.pk, mode)
