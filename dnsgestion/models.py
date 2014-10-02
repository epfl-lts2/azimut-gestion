from django.db import models

from servers.models import Server


class Zone(models.Model):
    name = models.CharField(max_length=255, help_text="No dot at the end")

    server = models.ForeignKey(Server)

    name_server = models.CharField(max_length=255)
    contact_email = models.EmailField()

    default_ttl = models.PositiveIntegerField(default=3600, help_text="Default expiration time")
    serial = models.PositiveIntegerField(default=2014010100)
    refresh = models.PositiveIntegerField(default=21600, help_text="Refresh time from slaves")
    retry = models.PositiveIntegerField(default=900, help_text="Delay to refresh if slave cannot access the server")
    expiry = models.PositiveIntegerField(default=604800, help_text="TTL of data for slaves if master cannot be contacted")
    negative_ttl = models.PositiveIntegerField(default=86400, help_text="Negative caching time")

    def __unicode__(self):
        return self.name

    def entries(self):
        return self.entry_set.order_by('disabled', 'order')

    def reorder(self):

        cid = 0

        for e in self.entries():
            e.order = cid
            e.save()
            cid += 1


class Entry(models.Model):

    zone = models.ForeignKey(Zone)

    disabled = models.BooleanField(default=False)

    label = models.CharField(max_length=255)

    CLASS_CHOICES = (
        ('IN', 'IN'),
        ('HS', 'HS'),
        ('CH', 'CH')
    )

    entry_class = models.CharField(max_length=12, choices=CLASS_CHOICES, default='IN')

    TYPE_CHOICES = (
        ('A', 'A - IPv4 Address record.'),
        ('AAAA', 'AAAA - IPv6 Address record.'),
        ('NS', 'NS - Name Server.'),
        ('CNAME', 'CNAME - Canonical Name.'),
        ('MX', 'MX - Mail Exchanger.'),
        ('TXT', 'TXT - Text information.'),
        ('PTR', 'PTR - IP address (IPv4 or IPv6) to host.'),
        ('SRV', 'SRV - Service.'),
        ('SPF', 'SPF - Sender Policy Framework (v1)'),
        ('DNSKEY', 'DNSKEY - DNS public key RR.'),
        ('DS', 'DS - Delegated Signer RR.'),
        ('NSEC', 'NSEC - Next Secure record.'),
        ('RRSIG', 'RRSIG - Signed RRset.'),
        ('KEY', 'KEY - Public key.')
    )

    entry_type = models.CharField(max_length=12, choices=TYPE_CHOICES, default='A')

    value = models.CharField(max_length=1024)

    order = models.PositiveIntegerField()
