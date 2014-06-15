from celery import task

import re
from django.utils import timezone

from backups.models import Backup, BackupRun, BackupSetOfRun

import os
from django.conf import settings

from app.utils import DjangoLock


@task(ignore_result=True)
def run_backup(id, mode='hourly', backupsetpk=None):
    """Run a backup"""

    backup = Backup.objects.get(pk=id)

    # Create the run
    backuprun = BackupRun(backup=backup, start_date=timezone.now())
    backuprun.save()

    def _notify_set_if_needed():
        if backupsetpk:
            check_end_of_backupset.delay(backupsetpk, backuprun.pk)

    # Backup
    if not backup.server_to.ssh_connection_string_from_gestion:
        print("Error: No connection from gestion")
        _notify_set_if_needed()
        return

    if not backup.server_from.ssh_connection_string_from_backup:
        print("Error: No connection from backup")
        _notify_set_if_needed()
        return

    os.system('ssh ' + backup.server_to.ssh_connection_string_from_gestion + ' wget ' + settings.GESTION_URL + 'backups/get_conf/' + str(backup.pk) + '/ -O /tmp/azimut-gestion-backup-config-' + str(backup.pk))

    to_do_string = ['rsnapshot -c /tmp/azimut-gestion-backup-config-' + str(backup.pk) + ' -v ' + mode]

    import subprocess
    p = subprocess.Popen(['ssh'] + backup.server_to.ssh_connection_string_from_gestion.split(' ') + [' '.join(to_do_string)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out, err = p.communicate()

    # import time
    # time.sleep(10)
    # out, err = "1", "2"

    backuprun.end_date = timezone.now()
    backuprun.stdout = out
    backuprun.stderr = err

    try:
        backuprun.nb_files = re.search('Number of files: (\d*)', out).group(1) or 0
    except:
        print("Error getting nb files")
        pass
    try:
        backuprun.size = re.search('Total file size: (\d*)', out).group(1) or 0
    except:
        print("Error getting total file size")
        pass

    backuprun.save()

    _notify_set_if_needed()


@task(ignore_result=True)
def run_active_backups(mode):
    """Run all actives backups"""

    # If we're in hourly mode, check that the previous backup was done. (In
    # othercases, it's ok to run more than one at a time)
    if mode == 'hourly':
        oldbackupruns = BackupSetOfRun.objects.filter(type='hourly', status='running').all()

        if oldbackupruns:
            # TODO: Create a warning
            print("Aborting run as there is still backup runnning !")
            return

    backups_to_run = Backup.objects.filter(active=True).all()

    backupset = BackupSetOfRun(type=mode)
    backupset.save()

    for bpk in backups_to_run:
        backupset.backups.add(bpk)

    backupset.save()

    for bkp in backups_to_run:
        run_backup.delay(bkp.pk, mode, backupset.pk)


@task(ignore_result=True)
def check_end_of_backupset(backupsetpk, backuprunpk):

    l = DjangoLock(settings.BACKUP_SET_LOCK)

    l.acquire()

    backupset = BackupSetOfRun.objects.get(pk=backupsetpk)
    backuprun = BackupRun.objects.get(pk=backuprunpk)

    try:

        backupset.backups.remove(backuprun.backup)
        backupset.backupruns.add(backuprun)

        backupset.total_size += backuprun.size
        backupset.total_files += backuprun.nb_files

        if not backupset.backups.all():  # End :)
            backupset.end_date = timezone.now()
            backupset.status = 'done'

            # TODO: Send mail ?

        backupset.save()

    except Exception as e:
        print("Error during check end of backup set !" + str(e))

    l.release()
