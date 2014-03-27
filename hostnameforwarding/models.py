from django.db import models

from servers.models import Server


class Hostnameforwarded(models.Model):
    server_host = models.ForeignKey(Server, related_name='hoststoforward')
    server_to = models.ForeignKey(Server, related_name='hostforwarded')
    domain = models.CharField(max_length=255)

    port_from = models.IntegerField(default=80)
    port_to = models.IntegerField(default=80)

    force_https = models.BooleanField(default=False)

    custom_https_certificate_pem = models.CharField(max_length=255, default='', blank=True, null=True)
    custom_https_certificate_key = models.CharField(max_length=255, default='', blank=True, null=True)

    def clean(self):
        from django.core.exceptions import ValidationError

        # Server host and to must match
        if self.server_to.vm_host != self.server_host:
            raise ValidationError('The VM is not hosted on the specified host.')
