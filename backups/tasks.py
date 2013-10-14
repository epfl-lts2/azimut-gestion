from celery import task

import re
from django.utils import timezone

from backups.models import Backup, BackupRun


@task(ignore_result=True)
def run_backup(id):
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

    to_do_string = ['rsync', '-a', '--stats', '--delete']

    cox_string = backup.server_from.ssh_connection_string_from_backup.split(' ')

    if '-p' in cox_string:

        next_is_port = False
        for x in cox_string:
            if next_is_port:
                next_is_port = False
                to_do_string += ['--rsh=\'ssh -p ' + x + '\'']

            if x == '-p':
                next_is_port = True

        cox = cox_string[-1]
    else:
        cox = cox_string[-1]

    if backup.prox_and_sys_excludes:
        to_do_string += ['--exclude=/proc', '--exclude=/sys']

    if backup.excludes:
        for folder in backup.excludes.split(','):
            to_do_string += ['--exclude=' + folder]

    to_do_string += [cox + ':' + backup.folder_from, backup.folder_to]

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
def run_active_backups():
    """Run all actives backups"""

    for bkp in Backup.objects.filter(active=True).all():
        run_backup.delay(bkp.pk)
