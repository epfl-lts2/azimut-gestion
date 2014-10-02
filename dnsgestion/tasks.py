from celery import task

from servers.models import Server
import os
from django.conf import settings


@task(ignore_result=True)
def update_dns(pk):
    """Update all server with taskforwarding info"""

    server = Server.objects.get(pk=pk)

    os.system('ssh ' + server.ssh_connection_string_from_gestion + ' wget ' + settings.GESTION_URL + 'dns/config/' + str(server.pk) + '/main/' + settings.DNS_SECRET + ' -O /etc/bind/named.conf.gestion')

    for z in server.zone_set.all():
        os.system('ssh ' + server.ssh_connection_string_from_gestion + ' wget ' + settings.GESTION_URL + 'dns/config/' + str(z.pk) + '/zone/' + settings.DNS_SECRET + ' -O /etc/bind/db.generated.' + z.name)

    os.system('ssh ' + server.ssh_connection_string_from_gestion + ' service bind9 restart')
