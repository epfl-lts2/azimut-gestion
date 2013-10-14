from django.db import models

from servers.models import Server


class Portforwarded(models.Model):
    server_host = models.ForeignKey(Server, related_name='portstoforward')
    server_to = models.ForeignKey(Server, related_name='portsforwared')
    port_from = models.IntegerField()
    port_to = models.IntegerField()

    PROTOCOL_CHOICES = (
        ('tcp', 'TCP'),
        ('udp', 'UDP')
        )

    protocol = models.CharField(max_length=7, choices=PROTOCOL_CHOICES)

    def clean(self):
        from django.core.exceptions import ValidationError
        # Server host and to must match

        if self.server_to.vm_host != self.server_host:
            raise ValidationError('The VM is not hosted on the specified host.')
