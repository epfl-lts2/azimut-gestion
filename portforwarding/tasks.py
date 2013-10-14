from celery import task

from servers.models import Server
import os
from django.conf import settings


@task(ignore_result=True)
def update_portforwarding():
    """Update all server with portforwarding"""

    for server in Server.objects.filter(is_vm=False).exclude(ssh_connection_string_from_gestion=None).exclude(ssh_connection_string_from_gestion='').exclude(external_interface='').all():

        os.system('ssh ' + server.ssh_connection_string_from_gestion + ' wget ' + settings.GESTION_URL + 'portforwarding/get_script/' + str(server.pk) + '/nat-vz -O /etc/init.d/nat-vz')
        os.system('ssh ' + server.ssh_connection_string_from_gestion + ' chmod +x /etc/init.d/nat-vz')
        os.system('ssh ' + server.ssh_connection_string_from_gestion + ' /etc/init.d/nat-vz flush')
        os.system('ssh ' + server.ssh_connection_string_from_gestion + ' /etc/init.d/nat-vz start')
