from django.db import models

from servers.models import Server
from django.utils import timezone

from django.contrib.auth.models import User

from django.core.mail import send_mail


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

    TYPE_CHOICES = (
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    )

    type = models.CharField(max_length=16, choices=TYPE_CHOICES)

    def not_too_old(self):
        from django.utils import timezone
        import datetime
        return (self.end_date + datetime.timedelta(days=3)) > timezone.now()


class BackupSetOfRun(models.Model):

    TYPE_CHOICES = (
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    )

    type = models.CharField(max_length=16, choices=TYPE_CHOICES)

    STATUS_CHOICES = (
        ('running', 'Running'),
        ('done', 'Done'),
        ('canceled', 'Cancelled'),
    )

    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='running')

    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(blank=True, null=True)

    backupruns = models.ManyToManyField(BackupRun)
    backups = models.ManyToManyField(Backup)

    total_size = models.BigIntegerField(default=0)
    total_files = models.BigIntegerField(default=0)

    def get_status_label(self):
        VALUES = {'running': 'warning', 'done': 'success', 'canceled': 'important'}

        if self.status in VALUES:
            return VALUES[self.status]
        else:
            return 'important'

    def get_total_time(self):
        if not self.end_date:
            end_date = timezone.now()
        else:
            end_date = self.end_date

        return int((end_date - self.start_date).total_seconds() / 36.0) / 100.0

    def get_total_time_label(self):

        tt = self.get_total_time()

        if tt < 3.5:
            return 'success'
        if tt < 4.0:
            return 'warning'
        return 'important'


class BackupNotification(models.Model):

    when = models.DateTimeField(auto_now_add=True)

    TYPE_CHOICES = (
        ('bkpdone', 'Backup completed'),
        ('bkpsetdone', 'Set of backup completed'),
        ('bkpsetnotstarted', 'Set of backup not started'),
        ('bkpsetcanceled', 'Set of backup canceled'),
        ('bkpfailled', 'Backup failled'),
    )

    type = models.CharField(max_length=32, choices=TYPE_CHOICES)

    message = models.TextField()

    VALUES = {'bkpdone': 'success', 'bkpsetdone': 'success', 'bkpsetnotstarted': 'important', 'bkpfailled': 'important', 'bkpsetcanceled': 'warning'}

    @staticmethod
    def get_types_with_labels():
        retour = []

        for (key, text) in BackupNotification.TYPE_CHOICES:
            retour.append((key, text, BackupNotification.VALUES[key]))

        return retour

    def get_type_label(self):

        if self.type in self.VALUES:
            return self.VALUES[self.type]
        else:
            return 'important'

    def send_notifications(self):

        subject = "Notification from AzimutGestion: %s" % (self.get_type_display(), )

        recpts = [buwwn.user.email for buwwn in BackupUserWhoWantNotifs.objects.filter(type=self.type).all()]

        send_mail(subject, self.message, 'noreply@azimut-prod.com', recpts, True)


class BackupUserWhoWantNotifs(models.Model):

    type = models.CharField(max_length=32, choices=BackupNotification.TYPE_CHOICES)
    user = models.ForeignKey(User)
