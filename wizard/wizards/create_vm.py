from _wizard import _Wizard

from django import forms

from django.conf import settings

import time
from django.utils import timezone

from servers.models import Server, ServerUser
from proxmoxs.views import check_if_ip_exists, gimme_prox_cox, get_templates
from backups.models import Backup
from groups.models import Group
from portforwarding.models import Portforwarded
from portforwarding.tasks import update_portforwarding
from hostnameforwarding.models import Hostnameforwarded
from hostnameforwarding.tasks import update_hostnameforwarding
from fabrun.models import Task
from fabrun.tasks import run_task
from backups.tasks import run_backup


class Step1Form(forms.Form):
    name = forms.CharField(help_text='Not the full domain, only the machine name')
    proxmox = forms.ModelChoiceField(queryset=Server.objects.filter(is_proxmox=True).order_by('name'))

    def clean(self):
        """Check if the name is unique"""

        full_name = self.get_full_name()

        if Server.objects.filter(name=full_name).count():
            raise forms.ValidationError("A VM with this name already exists !")

        return self.cleaned_data

    def get_full_name(self):
        """Return the full name for the VM"""

        if self.cleaned_data['proxmox'].hostname_for_vms_creation:
            return self.cleaned_data['name'] + '.' + self.cleaned_data['proxmox'].hostname_for_vms_creation
        else:
            return self.cleaned_data['name'] + '.' + self.cleaned_data['proxmox'].name



class Step2Form(forms.Form):
    add_to_groups = forms.BooleanField(initial=True, required=False)
    add_groups = forms.BooleanField(initial=True, required=False)
    create_vm = forms.BooleanField(initial=True, required=False)
    execute_setup_script = forms.BooleanField(initial=True, required=False)
    setup_portfowarding = forms.BooleanField(initial=True, required=False)
    setup_hostforwarding = forms.BooleanField(initial=True, required=False)
    setup_backups = forms.BooleanField(initial=True, required=False)
    do_first_backup = forms.BooleanField(initial=True, required=False)

    name = forms.CharField()
    keymanager_name = forms.CharField()
    internal_ip = forms.CharField()
    ssh_port = forms.CharField()
    ssh_for_gestion = forms.CharField()
    ssh_for_backups = forms.CharField()
    name_for_hostname_forwarding = forms.CharField()
    groups_membership = forms.CharField(initial=settings.CREATEVM_DEFAULT_GROUPS)
    groups_allowed = forms.CharField(initial=settings.CREATEVM_DEFAULT_GROUPS_ALLOWED)
    backup_source = forms.CharField(initial='/')
    backup_proc_and_sys_excludes = forms.BooleanField(initial=True, required=False)
    backup_excludes = forms.CharField(required=False)
    backup_destination = forms.CharField()
    users = forms.CharField(initial='root')
    ram = forms.IntegerField(help_text='Mb', initial="512", min_value=256)
    swap = forms.IntegerField(help_text='Mb', initial="512", min_value=0)
    disk = forms.IntegerField(help_text='Gb', initial="10", min_value=5)
    cpus = forms.IntegerField(initial="1", min_value=1)
    template = forms.ChoiceField()

    def __init__(self, server, name, build_inital_values, *args, **kwargs):
        super(Step2Form, self).__init__(*args, **kwargs)

        self.server = server

        if build_inital_values:

            self.fields["name"].initial = name
            self.fields["keymanager_name"].initial = name
            self.fields["name_for_hostname_forwarding"].initial = name
            self.fields['backup_destination'].initial = settings.BACKUP_BASE_FOLDER + name + '/'

            used_ip = []

            for vm in gimme_prox_cox(server.ip_for_proxmox()).getNodeContainerIndex(server.proxmox_node_name)['data']:
                used_ip.append(vm['ip'])

            to_use_ip = None
            ip_id = None

            for i in range(1, 255):
                ip = settings.PROXMOX_IP_BASE + str(i)

                if ip not in used_ip:
                    to_use_ip = ip
                    ip_id = i

                    break

            if to_use_ip:
                self.fields["internal_ip"].initial = to_use_ip

                ssh_port = str(100 + ip_id) + '22'

                self.fields["ssh_port"].initial = ssh_port

                if server.external_hostname_for_vms_creation:
                    name_to_use = server.external_hostname_for_vms_creation
                else:
                    name_to_use = server.name

                self.fields['ssh_for_backups'].initial = '-p ' + ssh_port + ' root@' + name_to_use

                if server.name == settings.GESTION_VM_NAME:
                    self.fields['ssh_for_gestion'].initial = 'root@' + to_use_ip
                else:
                    self.fields['ssh_for_gestion'].initial = self.fields['ssh_for_backups'].initial

        self.fields['template'].choices = get_templates(gimme_prox_cox(server.ip_for_proxmox()), server)

    def clean(self):
        """Check if dependencies between tasks is ok"""

        if self.cleaned_data['execute_setup_script'] and not self.cleaned_data['create_vm']:
            raise forms.ValidationError("VM must be created to execute the setup script")

        if self.cleaned_data['execute_setup_script'] and not self.cleaned_data['setup_portfowarding']:
            raise forms.ValidationError("Port forwarding must be setup to execute the setup script")

        if self.cleaned_data['do_first_backup'] and not self.cleaned_data['execute_setup_script']:
            raise forms.ValidationError("Setup script must be executed to do the fisrt backup")

        if self.cleaned_data['do_first_backup'] and not self.cleaned_data['add_groups']:
            raise forms.ValidationError("Groups must be added to do the fisrt backup")

        #Check ip
        if 'internal_ip' in self.cleaned_data and not check_if_ip_exists(gimme_prox_cox(self.server.ip_for_proxmox()), self.server, self.cleaned_data['internal_ip']):
            raise forms.ValidationError("The IP is already used on the server")

        #Check if backup is unique
        if self.cleaned_data['setup_backups']:
            backup_server = Server.objects.get(name=settings.BACKUP_SERVER)
            if 'backup_destination' in self.cleaned_data and Backup.objects.filter(server_to=backup_server, folder_to=self.cleaned_data['backup_destination']).count():
                raise forms.ValidationError("Destionation folder already used on the backup server")

        #Check if name is unique
        if 'name' in self.cleaned_data and Server.objects.filter(name=self.cleaned_data['name']).count():
            raise forms.ValidationError('Server name not unique')

        if 'keymanager_name' in self.cleaned_data and Server.objects.filter(keymanger_name=self.cleaned_data['keymanager_name']).count():
            raise forms.ValidationError('Server name not unique')

        return self.cleaned_data


class CreateVm(_Wizard):
    """Simple wizard to create a VM"""

    _name = 'CreateVm'
    _description = 'Simple wizard to create a VM'

    _nb_step = 2
    _nb_task = 9

    _steps_names = ['VM Name and Host', 'Advanced parameters']
    _tasks_names = ['Create server', 'Setup VM groups', 'Create VM', 'Start VM', 'Open ports', 'Forward domain', 'Execute setup script', 'Create backup task', 'Execute backup task']

    def display_step_1(self, request):

        if request.method == 'POST':
            form = Step1Form(request.POST)
        else:
            form = Step1Form()

        return ('', form, "$('#id_proxmox').css('width', '220px').select2();")

    def save_step_1(self, form):
        full_name = form.get_full_name()
        server_host_pk = form.cleaned_data['proxmox'].pk

        return {'name': full_name, 'server_host_pk': server_host_pk}

    def display_step_2(self, request):

        server = Server.objects.get(pk=self.step_data[0]['server_host_pk'])
        name = self.step_data[0]['name']

        if request.method == 'POST':
            form = Step2Form(server, name, False, request.POST)
        else:
            form = Step2Form(server, name, True)

        return ('If needed, you can edit values of this forms. You can leave them to defaults values, everything should be ok !', form, "$('#id_template').css('width', '220px').select2();")

    def save_step_2(self, form):
        return form.cleaned_data

    def do_task_1(self):
        """Create the server with corrects parameters"""

        srv = Server()
        srv.name = self.step_data[1]['name']
        srv.keymanger_name = self.step_data[1]['keymanager_name']
        srv.is_vm = True
        srv.external_ip = ''
        srv.internal_ip = self.step_data[1]['internal_ip']
        srv.vm_host = Server.objects.get(pk=self.step_data[0]['server_host_pk'])

        srv.ssh_connection_string_from_gestion = self.step_data[1]['ssh_for_gestion']
        srv.ssh_connection_string_from_backup = self.step_data[1]['ssh_for_backups']

        srv.is_proxmox = False
        srv.save()

        for user in self.step_data[1]['users'].split(','):
            ServerUser(server=srv, name=user).save()

        return (True, {'server_pk': srv.pk})

    def do_task_2(self):
        """Add the VM to corrects groups"""

        srv = Server.objects.get(pk=self.task_data[0]['server_pk'])

        if self.step_data[1]['add_to_groups']:

            for grp in self.step_data[1]['groups_membership'].split(','):
                try:
                    group = Group.objects.get(name=grp)
                    group.servers.add(srv)
                    group.save()

                except Group.DoesNotExist:
                    print "Cannot find group " + grp
                    return (False, None)

        if self.step_data[1]['add_groups']:

            for grp in self.step_data[1]['groups_allowed'].split(','):
                try:
                    group = Group.objects.get(name=grp)
                    group.allowed_servers.add(srv)
                    group.save()

                except Group.DoesNotExist:
                    print "Cannot find group " + grp
                    return (False, None)

        return (True, None)

    def wait_end_of_task(self, com, node, retour):
        if retour['data']:
            while True:
                status = com.getNodeTaskStatusByUPID(node, retour['data'])
                if status['data']['status'] == 'running':
                    time.sleep(1)
                else:
                    return True
        return False

    def do_task_3(self):
        """Create the VM on the proxmox server"""

        srv = Server.objects.get(pk=self.task_data[0]['server_pk'])

        if self.step_data[1]['create_vm']:

            com = gimme_prox_cox(srv.vm_host.ip_for_proxmox())

            id = com.getClusterVmNextId()['data']

            post_data = {'ostemplate': self.step_data[1]['template'], 'vmid': id, 'cpus': self.step_data[1]['cpus'], 'description': 'fabric-manual-from-wizard',
                         'disk': self.step_data[1]['disk'], 'hostname': srv.name, 'memory': self.step_data[1]['ram'],
                         'password': srv.random_proxmox_password(), 'swap': self.step_data[1]['swap'], 'ip_address': srv.internal_ip, 'storage': settings.CREATE_VM_STORAGE}

            retour = com.createOpenvzContainer(srv.vm_host.proxmox_node_name, post_data)

            return (self.wait_end_of_task(com, srv.vm_host.proxmox_node_name, retour), {'vm_id': id})

        return (True, None)

    def do_task_4(self):
        """Start the VM on the proxmox server"""

        srv = Server.objects.get(pk=self.task_data[0]['server_pk'])

        if self.step_data[1]['create_vm']:

            com = gimme_prox_cox(srv.vm_host.ip_for_proxmox())

            retour = com.startOpenvzContainer(srv.vm_host.proxmox_node_name, self.task_data[2]['vm_id'])

            return (self.wait_end_of_task(com, srv.vm_host.proxmox_node_name, retour), None)

        return (True, None)

    def do_task_5(self):
        """Open ports for the VM"""

        srv = Server.objects.get(pk=self.task_data[0]['server_pk'])

        if self.step_data[1]['setup_portfowarding']:

            Portforwarded(server_host=srv.vm_host, server_to=srv, port_from=self.step_data[1]['ssh_port'], port_to=22, protocol='tcp').save()

            update_portforwarding()

        return (True, None)

    def do_task_6(self):
        """Forward the domain for the server"""

        srv = Server.objects.get(pk=self.task_data[0]['server_pk'])

        if self.step_data[1]['setup_hostforwarding']:

            if settings.NGNIX_SSL_KEY != '':
                Hostnameforwarded(server_host=srv.vm_host, server_to=srv, domain=self.step_data[1]['name_for_hostname_forwarding'], port_from=443).save()

            Hostnameforwarded(server_host=srv.vm_host, server_to=srv, domain=self.step_data[1]['name_for_hostname_forwarding']).save()
            update_hostnameforwarding()

        return (True, None)

    def do_task_7(self):
        """Execute the setup script"""

        srv = Server.objects.get(pk=self.task_data[0]['server_pk'])

        if self.step_data[1]['execute_setup_script']:
            t = Task(creation_date=timezone.now(), server=srv, command=settings.SETUP_FABRIC_SCRIPT)
            t.save()
            run_task(t.pk)

        return (True, None)

    def do_task_8(self):
        """Create the backup task"""

        srv = Server.objects.get(pk=self.task_data[0]['server_pk'])

        if self.step_data[1]['setup_backups']:
            bkp = Backup()
            bkp.name = self.step_data[1]['name']
            bkp.server_from = srv
            bkp.server_to = Server.objects.get(name=settings.BACKUP_SERVER)
            bkp.folder_from = self.step_data[1]['backup_source']
            bkp.folder_to = self.step_data[1]['backup_destination']
            bkp.prox_and_sys_excludes = self.step_data[1]['backup_proc_and_sys_excludes']
            bkp.excludes = self.step_data[1]['backup_excludes']
            bkp.active = True

            bkp.save()

            return (True, {'bkp_pk': bkp.pk})

        return (True, None)

    def do_task_9(self):
        """Backup the server"""
        if self.step_data[1]['do_first_backup']:

            id = self.task_data[7]['bkp_pk']

            run_backup(id)

        return (True, None)
