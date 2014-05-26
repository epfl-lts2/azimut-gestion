
from _wizard import _Wizard

from django import forms

from django.conf import settings

from django.utils import timezone

from servers.models import Server
import os
import uuid
import re


class Step1Form(forms.Form):
    name = forms.CharField(help_text='The name of the database and the user. This will be prefixed with the VM name')
    password = forms.CharField(widget=forms.PasswordInput(), required=False, help_text='Leave blank to generate a random password')
    save_in_notes = forms.BooleanField(help_text='Check this to save the password in the server\'s note')
    server = forms.ModelChoiceField(queryset=Server.objects.exclude(ssh_connection_string_from_gestion=None).order_by('name'))


class CreateMysqlTable(_Wizard):
    """Simple wizard to create a mysql table"""

    _name = 'CreateMysqlTable'
    _description = 'Simple wizard to create a mysql table and a linked user'

    _nb_step = 1
    _nb_task = 5

    _steps_names = ['Informations needed']
    _tasks_names = ['Create database', 'Create mysql user', 'Grand rights on the server', 'Flush privileges', 'Save data']

    def display_step_1(self, request):

        if request.method == 'POST':
            form = Step1Form(request.POST)
        else:
            form = Step1Form()

        return ('', form, "$('#id_server').css('width', '220px').select2();")

    def save_step_1(self, form):
        server = Server.objects.get(pk=form.cleaned_data['server'].pk)
        name = re.sub('[\W_]+', '', server.name) + '_' + form.cleaned_data['name']
        server_pk = form.cleaned_data['server'].pk
        password = form.cleaned_data['password']
        save_in_notes = form.cleaned_data['save_in_notes']

        if not password:
            password = str(uuid.uuid4())

        return {'name': name, 'server_pk': server_pk, 'password': password, 'save_in_notes': save_in_notes}

    def do_task_1(self):
        """Create the database"""

        server = Server.objects.get(pk=self.step_data[0]['server_pk'])

        # Find the mysql server
        try:
            server_mysql = server.vm_host.mysql_server
        except:
            return (False, None)

        os.system('ssh ' + server_mysql.ssh_connection_string_from_gestion + ' "echo \'CREATE DATABASE %s DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;\' | mysql --user=\'%s\' --password=\'%s\'"' % (self.step_data[0]['name'], settings.MYSQL_USERNAME, settings.MYSQL_PASSWORD))

        return (True, None)

    def do_task_2(self):
        """Create the mysql user"""

        server = Server.objects.get(pk=self.step_data[0]['server_pk'])
        server_mysql = server.vm_host.mysql_server

        os.system('ssh ' + server_mysql.ssh_connection_string_from_gestion + ' "echo \'CREATE USER %s@%s IDENTIFIED BY \\"%s\\";\' | mysql --user=\'%s\' --password=\'%s\'"' % (self.step_data[0]['name'], server.internal_ip, self.step_data[0]['password'], settings.MYSQL_USERNAME, settings.MYSQL_PASSWORD))

        return (True, None)

    def do_task_3(self):
        """Grand rights on the server"""

        server = Server.objects.get(pk=self.step_data[0]['server_pk'])
        server_mysql = server.vm_host.mysql_server

        os.system('ssh ' + server_mysql.ssh_connection_string_from_gestion + ' "echo \'GRANT ALL ON %s.* TO %s@%s;\' | mysql --user=\'%s\' --password=\'%s\'"' % (self.step_data[0]['name'], self.step_data[0]['name'], server.internal_ip, settings.MYSQL_USERNAME, settings.MYSQL_PASSWORD))

        return (True, None)

    def do_task_4(self):
        """Flush privileges"""

        server = Server.objects.get(pk=self.step_data[0]['server_pk'])
        server_mysql = server.vm_host.mysql_server

        os.system('ssh ' + server_mysql.ssh_connection_string_from_gestion + ' "echo \'FLUSH PRIVILEGES;\' | mysql --user=\'%s\' --password=\'%s\'"' % (settings.MYSQL_USERNAME, settings.MYSQL_PASSWORD))

        return (True, None)

    def do_task_5(self):
        """Save data"""

        if self.step_data[0]['save_in_notes']:
            server = Server.objects.get(pk=self.step_data[0]['server_pk'])

            if not server.notes:
                server.notes = ""

            server.notes += """
    ==MysqlDB Created %s==
    Mysql database: %s
    Mysql username: %s
    Mysql password: %s""" % (str(timezone.now()), self.step_data[0]['name'], self.step_data[0]['name'], self.step_data[0]['password'])
            server.save()

        return (True, None)
