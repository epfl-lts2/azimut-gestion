from celery import task

from servers.models import Server
import os
from django.conf import settings


@task(ignore_result=True)
def update_hostnameforwarding():
    """Update all server with taskforwarding info"""

    for server in Server.objects.filter(is_vm=False).exclude(ngnix_server=None).exclude(ngnix_server__ssh_connection_string_from_gestion=None).exclude(ngnix_server__ssh_connection_string_from_gestion='').all():

        os.system('ssh ' + server.ngnix_server.ssh_connection_string_from_gestion + ' wget ' + settings.GESTION_URL + 'hostnameforwarding/get_conf/' + str(server.pk) + '/ngnix.conf -O /etc/nginx/sites-available/ngnix.conf')
        os.system('ssh ' + server.ngnix_server.ssh_connection_string_from_gestion + ' /etc/init.d/nginx reload')
