from django.db import models

from servers.models import Server


class Task(models.Model):
    """A task"""

    creation_date = models.DateTimeField()
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    stdout = models.TextField()
    stderr = models.TextField()

    server = models.ForeignKey(Server)
    command = models.TextField()

    args = models.TextField()
