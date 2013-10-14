from django.db import models

from servers.models import Server


class Backup(models.Model):

    name = models.CharField(max_length=255)

    server_from = models.ForeignKey(Server, related_name='backups_of_the_server')
    server_to = models.ForeignKey(Server, related_name='backups_on_the_server')

    folder_from = models.CharField(max_length=255)
    folder_to = models.CharField(max_length=255)

    prox_and_sys_excludes = models.BooleanField(default=True, help_text="Exclude /proc and /sys")
    excludes = models.TextField(help_text='Comma-separted list of folder, relative to folder_from', blank=True, null=True)

    active = models.BooleanField()

    def get_last_run(self):
        """Return the last run of the backup (or None)"""

        if self.backuprun_set.count() > 0:
            return self.backuprun_set.order_by('-start_date').all()[0]


class BackupRun(models.Model):

    backup = models.ForeignKey(Backup)

    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)

    size = models.BigIntegerField(default=0)
    nb_files = models.BigIntegerField(default=0)

    stdout = models.TextField(blank=True, null=True)
    stderr = models.TextField(blank=True, null=True)

    def not_too_old(self):
        from django.utils import timezone
        import datetime
        return (self.end_date + datetime.timedelta(days=3)) > timezone.now()
