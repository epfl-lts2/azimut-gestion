from celery import task

from servers.models import Server
import os
from django.conf import settings
import subprocess


@task(ignore_result=True)
def update_samba():
    """Update all samba server with new infos"""

    for server in Server.objects.filter(samba_management=True).exclude(ssh_connection_string_from_gestion=None).exclude(ssh_connection_string_from_gestion='').all():

        # Sync users
        #  Get user list
        users_in_system = []

        result = subprocess.check_output('ssh ' + server.ssh_connection_string_from_gestion + ' cat /etc/passwd | cut -d: -f1', shell=True)

        for user in result.split():
            if user[:len(settings.SAMBA_USER_PREFIX)] == settings.SAMBA_USER_PREFIX:
                users_in_system.append(user)

        # Add new users
        for share in server.share_set.all():
            if share.get_username() not in users_in_system:
                print "Adding " + share.get_username()
                os.system('ssh ' + server.ssh_connection_string_from_gestion + ' useradd -s /bin/true ' + share.get_username())
            else:
                users_in_system.remove(share.get_username())

        #  Users to be deleted
        for user in users_in_system:
            print "Removing " + share.get_username()
            os.system('ssh ' + server.ssh_connection_string_from_gestion + ' deluser ' + user)

        # Set users passwords, create folders and set rights
        for share in server.share_set.all():
            os.system('ssh ' + server.ssh_connection_string_from_gestion + ' "(echo \'' + share.get_password() + '\'; echo \'' + share.get_password() + '\')| smbpasswd -a ' + share.get_username() + ' -s"')
            os.system('ssh ' + server.ssh_connection_string_from_gestion + ' mkdir -p ' + share.get_full_path())
            os.system('ssh ' + server.ssh_connection_string_from_gestion + ' chown ' + share.get_username() + ' ' + share.get_full_path())

        # Update config file
        os.system('ssh ' + server.ssh_connection_string_from_gestion + ' wget ' + settings.GESTION_URL + 'samba/' + str(server.pk) + '/config/ -O /etc/smb.shares.conf')

        # Reload config
        os.system('ssh ' + server.ssh_connection_string_from_gestion + ' /etc/init.d/samba reload')
