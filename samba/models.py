from django.db import models

from servers.models import Server

from django.conf import settings

import os
import hashlib
import string


class Share(models.Model):
    """A share"""

    server = models.ForeignKey(Server)

    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255, help_text='Relative path')

    def get_full_path(self):
        """Return the full path of the samba share"""

        # Remove the first slash
        path = self.path if self.path[0] != '/' else self.path[1:]

        return os.path.join(self.server.samba_base_folder, path)

    def get_username(self):
        """Return the username to use"""

        return settings.SAMBA_USER_PREFIX + self.name

    def get_password(self):
        """Return the password to use"""
        return filter(lambda x: x if x in string.ascii_letters + string.digits + '.,-' else '', hashlib.sha512(str(self.pk) + self.name + settings.SAMBA_SECRET_KEY).digest())
