from celery import task

from servers.models import Server
import os
from django.conf import settings
import subprocess
from logstash.models import Execution
import json
from proxmoxs.views import gimme_prox_cox


@task(ignore_result=True)
def do_autodetection(expk):
    """Do automatic detection of logstash config"""

    ex = Execution.objects.get(pk=expk)

    ex.output += 'Sarting execution\n'
    ex.save()

    def work_on_host(server, base_tags, base_path, no_vhost_check=True):
        """Work on host"""

        things_to_checks = []

        def check_file(file, type, file_tags):

            things_to_checks.append((base_path + file, type, file_tags + base_tags))

        def do_query(query):
            p = subprocess.Popen(['ssh'] + server.ssh_connection_string_from_gestion.split(' ') + ["cat - | sh"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=1)
            return p.communicate(query + '\nexit')[0].split()

        ex.output += '---Checking common files\n'
        ex.save()

        # Syslog
        check_file('/var/log/syslog', 'syslog', ['syslog'])

        # Auth.log
        check_file('/var/log/auth.log', 'syslog', ['auth.log'])

        # Apache logs
        ex.output += '---Checking apache logs\n'
        ex.save()

        for folder in ['apache2', 'httpd']:
            for prefix in ['', 'ssl_', 'others_vhost_']:
                for end in ['.log', '_log']:
                    for postfix in ['', '_ssl']:
                        check_file('/var/log/' + folder + '/' + prefix + 'access' + postfix + end, 'apachelog', ['access.log'])
                        check_file('/var/log/' + folder + '/' + prefix + 'error' + postfix + end, 'apachelog', ['error.log'])

        # Ngnix log
        ex.output += '---Checking ngnix logs\n'
        ex.save()

        check_file('/var/log/nginx.log', 'nginxlog', ['ngnix.log'])
        check_file('/var/log/error.log', 'nginxerrlog', ['ngnixerror.log'])

        # Mysql log
        ex.output += '---Checking mysql logs\n'
        ex.save()

        check_file('/var/log/mysql.log', 'mysqllog', ['mysql.log'])
        check_file('/var/log/mysql.err', 'mysqlerrlog', ['mysqlerror.log'])

        if not no_vhost_check:
            # Apache logs by vhost,
            ex.output += '---Checking apache logs in vhost folders\n'
            ex.save()

            base_list = do_query('for x in `ls /var/www/vhosts/*/logs/*/access_log`; do echo $x; done') + do_query('for x in `ls /var/www/vhosts/*/logs/access_log`; do echo $x; done')

            for elem in base_list:
                bpath = '/'.join(elem.split('/')[:-1]) + '/'
                tag = elem.split('/')[-2]

                check_file(bpath + 'access_log', 'apachelog', ['access.log', tag])
                check_file(bpath + 'access_ssl_log', 'apachelog', ['access.log', tag])
                check_file(bpath + 'error_log', 'apachelog', ['error.log', tag])

        # Do check in one pass
        entries_list = []

        output = do_query('\n'.join(['ls ' + x[0] + ' 2>/dev/null' for x in things_to_checks]))

        for (path, type, tags) in things_to_checks:

            if path in output:
                entries_list.append((path, type, ','.join(sorted(tags)), server.pk))
                ex.output += '---' + path + ': ' + type + '\n'

        ex.save()

        return entries_list

    retour = []

    # Get all shipper
    for s in Server.objects.filter(logstash_shipper=True).all():
        ex.output += 'Working on ' + s.name + '\n'
        ex.save()

        bn = s.name.split('.')[-2]

        tags = [bn, s.name]

        if s.is_proxmox:
            tags.append('proxmox')

        # Do normal checks
        retour += work_on_host(s, tags, '', no_vhost_check=s.is_proxmox)  # If not proxmox, check vhosts

        # If proxmox, check subvms
        if s.is_proxmox:

            vm_ids = {}

            proxretour = gimme_prox_cox(s.ip_for_proxmox()).getNodeContainerIndex(s.proxmox_node_name)

            if 'data' in proxretour:
                for elem in proxretour['data']:
                    vm_ids[elem['ip']] = elem['vmid']

            for proxmox in s.server_set.all():
                tags = [bn, proxmox.name, 'vm']

                if proxmox.internal_ip in vm_ids:
                    id = vm_ids[proxmox.internal_ip]

                    ex.output += 'Working on ' + proxmox.name + ', proxmox vm\n'
                    ex.save()

                    retour += work_on_host(s, tags, '/var/lib/vz/root/' + str(id))
                else:

                    ex.output += 'Cannot work on ' + proxmox.name + ', no id\n'
                    ex.save()

    ex.sugested_result = json.dumps(retour)

    ex.output += 'Done !\n'
    ex.done = True
    ex.save()
