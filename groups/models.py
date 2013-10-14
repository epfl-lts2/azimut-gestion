from django.db import models

from django.contrib.auth.models import User
from servers.models import Server, SshKey, ServerUser


class Group(models.Model):
    name = models.CharField(max_length=255)

    users = models.ManyToManyField(User, blank=True)
    servers = models.ManyToManyField(Server, blank=True)
    servers_keys = models.ManyToManyField(SshKey, blank=True, related_name='group_set')

    allowed_servers = models.ManyToManyField(Server, blank=True, related_name='groupwithaccess_set')
    allowed_servers_users = models.ManyToManyField(ServerUser, blank=True)

    def __unicode__(self):
        return self.name
