from django.db import models

from django.conf import settings

import hashlib


class Server(models.Model):
    name = models.CharField(max_length=255)
    keymanger_name = models.CharField(max_length=255, unique=True)

    is_vm = models.BooleanField()
    external_ip = models.IPAddressField(blank=True, null=True)
    internal_ip = models.IPAddressField(blank=True, null=True)
    vm_host = models.ForeignKey('Server', blank=True, null=True, related_name='server_set')
    ngnix_server = models.ForeignKey('Server', blank=True, null=True, related_name='ngnixed_server_set')

    ssh_connection_string_from_gestion = models.CharField(max_length=255, blank=True, null=True)
    ssh_connection_string_from_backup = models.CharField(max_length=255, blank=True, null=True)

    external_interface = models.CharField(max_length=15, blank=True, null=True)

    is_proxmox = models.BooleanField()
    proxmox_node_name = models.CharField(max_length=255, blank=True, null=True, default='')

    external_hostname_for_vms_creation = models.CharField(max_length=255, blank=True, null=True)
    hostname_for_vms_creation = models.CharField(max_length=255, blank=True, null=True, default='')

    samba_management = models.BooleanField(default=False)
    samba_base_folder = models.CharField(max_length=255, blank=True, null=True, default='')

    def all_ports(self):
        """Return all ports (forwarded from and to)"""

        liste = []

        for port in self.portstoforward.all():
            liste.append(port)

        for port in self.portsforwared.all():
            liste.append(port)

        return liste

    def all_hosts(self):
        """Return all hosts (forwarded from and to)"""

        liste = []

        for host in self.hoststoforward.all():
            liste.append(host)

        for host in self.hostforwarded.all():
            liste.append(host)

        return liste

    def __unicode__(self):
        return self.name

    def ip_for_proxmox(self):
        """Return IP to use for proxmox."""
        return self.ssh_connection_string_from_gestion.split('@')[-1]

    def get_host_for_fabric(self):
        """Return the host to use for fabric"""

        port = 22

        splited_cox = self.ssh_connection_string_from_gestion.split(' ')

        if '-p' in splited_cox:

            next_is_port = False
            for x in splited_cox:

                if next_is_port:
                    next_is_port = False
                    port = x

                if x == '-p':
                    next_is_port = True

            cox = splited_cox[-1]
        else:
            cox = splited_cox[-1]

        return cox + ':' + str(port)

    def get_port(self):
        """Get the port"""
        # Hack, but easy way :D
        return self.get_host_for_fabric().split(':')[-1]


    def random_proxmox_password(self):
        """Return a unique but hard to guess password for new VMs"""
        b = ''
        if self.vm_host:
            b = str(self.vm_host.pk)
        return hashlib.sha224(b + settings.VM_PASS_SECRET + str(self.pk)).hexdigest()

    def get_users_list(self):
        """Return the list of  users"""
        retour = ''

        for u in self.serveruser_set.all():
            retour += u.name + ','

        return retour[:-1]

    def last_runs(self):
        """Return the last runs of fabrics scripts"""
        return self.task_set.order_by('-creation_date').all()[:10]

    def get_vms(self):
        return self.server_set.order_by('name').all()


class ServerUser(models.Model):
    server = models.ForeignKey(Server)
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name + '@' + self.server.name


class SshKey(models.Model):
    server = models.ForeignKey(Server)
    user = models.CharField(max_length=255)

    key = models.TextField()

    def get_comment(self):
        bonus = ''

        if len(self.key.split(' ')) > 2:
            bonus = ' (' + self.key.split(' ')[2].strip() + ')'

        return 'Key #' + str(self.pk) + bonus

    def __unicode__(self):
        return self.user + '@' + self.server.name
