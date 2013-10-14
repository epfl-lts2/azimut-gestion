from django.db import models

from django.contrib.auth.models import User


class SshKey(models.Model):
    user = models.ForeignKey(User)
    key = models.TextField()

    def get_comment(self):
        bonus = ''

        if len(self.key.split(' ')) > 2:
            bonus = ' (' + self.key.split(' ')[2].strip() + ')'

        return 'Key #' + str(self.pk) + bonus
