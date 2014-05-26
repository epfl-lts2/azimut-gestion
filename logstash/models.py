from django.db import models


from servers.models import Server


class File(models.Model):
    """A file to monitor"""

    server = models.ForeignKey(Server)

    file = models.CharField(max_length=255)

    TYPE_CHOICES = (('apachelog', 'Apache log'), ('syslog', 'Syslog'), ('misc', 'Misc'))
    type = models.CharField(max_length=255, choices=TYPE_CHOICES)

    tags = models.CharField(max_length=512)

    def sorted_tags(self):
        """Return the list of tags, sorted"""
        return ','.join(sorted(self.tags.split(',')))

    


class Execution(models.Model):

    output = models.TextField()
    done = models.BooleanField(default=False)
    sugested_result = models.TextField()
