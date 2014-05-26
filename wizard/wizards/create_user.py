from _wizard import _Wizard

from django import forms

from django.conf import settings

from django.utils import timezone

from servers.models import Server, ServerUser
from fabrun.models import Task
from fabrun.tasks import run_task

import os


class Step1Form(forms.Form):
    name = forms.CharField(help_text='')
    password = forms.CharField(widget=forms.PasswordInput(), required=False, help_text='Leave blank to disable the password')
    server = forms.ModelChoiceField(queryset=Server.objects.exclude(ssh_connection_string_from_gestion=None).order_by('name'))


class CreateUser(_Wizard):
    """Simple wizard to create a user on a VM"""

    _name = 'CreateUser'
    _description = 'Simple wizard to create a new user on a server'

    _nb_step = 1
    _nb_task = 7

    _steps_names = ['User details']
    _tasks_names = ['Create user', 'Set password', 'Copy config scripts', 'Add user to the server', 'Create ssh folder', 'Update keymanager', 'Run keymanager']

    def display_step_1(self, request):

        if request.method == 'POST':
            form = Step1Form(request.POST)
        else:
            form = Step1Form()

        return ('', form, "$('#id_server').css('width', '220px').select2();")

    def save_step_1(self, form):
        name = form.cleaned_data['name']
        server_pk = form.cleaned_data['server'].pk
        password = form.cleaned_data['password']

        return {'name': name, 'server_pk': server_pk, 'password': password}

    def do_task_1(self):
        """Create the user"""

        server = Server.objects.get(pk=self.step_data[0]['server_pk'])

        os.system('ssh ' + server.ssh_connection_string_from_gestion + ' useradd -s /bin/zsh -m ' + self.step_data[0]['name'])

        return (True, None)

    def do_task_2(self):
        """Set the user password"""

        server = Server.objects.get(pk=self.step_data[0]['server_pk'])

        if self.step_data[0]['password'] != '':
            os.system('ssh ' + server.ssh_connection_string_from_gestion + ' "echo \'' + self.step_data[0]['name'] + ':' + self.step_data[0]['password'] + '\' | chpasswd"')

        return (True, None)

    def do_task_3(self):
        """Copy config scripts"""

        server = Server.objects.get(pk=self.step_data[0]['server_pk'])

        t = Task(creation_date=timezone.now(), server=server, command=settings.COPY_USER_CONFIG_FABRIC_SCRIPT, args=self.step_data[0]['name'])
        t.save()
        run_task(t.pk)

        return (True, None)

    def do_task_4(self):
        """Add user to the server"""

        server = Server.objects.get(pk=self.step_data[0]['server_pk'])

        ServerUser(server=server, name=self.step_data[0]['name']).save()

        return (True, None)

    def do_task_5(self):
        """Create the SSH folder"""

        server = Server.objects.get(pk=self.step_data[0]['server_pk'])

        os.system('ssh ' + server.ssh_connection_string_from_gestion + ' "mkdir ~' + self.step_data[0]['name'] + '/.ssh/"')
        os.system('ssh ' + server.ssh_connection_string_from_gestion + ' "chown ' + self.step_data[0]['name'] + ' ~' + self.step_data[0]['name'] + '/.ssh/"')

        return (True, None)

    def do_task_6(self):
        """Update the keymanager"""

        server = Server.objects.get(pk=self.step_data[0]['server_pk'])

        t = Task(creation_date=timezone.now(), server=server, command=settings.UPDATE_KM_FABRIC_SCRIPT)
        t.save()
        run_task(t.pk)

        return (True, None)

    def do_task_7(self):
        """Run the keymanager"""

        server = Server.objects.get(pk=self.step_data[0]['server_pk'])

        t = Task(creation_date=timezone.now(), server=server, command=settings.RUN_KM_FABRIC_SCRIPT)
        t.save()
        run_task(t.pk)

        return (True, None)
