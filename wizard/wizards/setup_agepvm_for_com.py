from _wizard import _Wizard

from django import forms

from django.conf import settings

from django.utils import timezone

from django.core.mail import send_mail

from servers.models import Server, ServerUser
from fabrun.models import Task
from fabrun.tasks import run_task

import os
import uuid

from hostnameforwarding.models import Hostnameforwarded
from hostnameforwarding.tasks import update_hostnameforwarding


class Step1Form(forms.Form):
    server = forms.ModelChoiceField(queryset=Server.objects.exclude(ssh_connection_string_from_gestion=None).order_by('name'))


class Step2Form(forms.Form):

    username = forms.CharField(help_text='Be nice and avoid strange chars here. [a-z] will be fine.')
    password = forms.CharField()

    grant_sudo_rights = forms.BooleanField(initial=False, required=False)
    
    create_mysql_database = forms.BooleanField(initial=True, required=False)
    mysql_password = forms.CharField()

    create_epfl_host = forms.BooleanField(initial=True, required=False)
    epfl_host = forms.CharField()

    send_confirmation_email = forms.BooleanField(initial=True, required=False)
    mail_dest = forms.CharField(help_text='Comma-separted values')

    def __init__(self, server, build_inital_values, request, *args, **kwargs):
        super(Step2Form, self).__init__(*args, **kwargs)

        self.server = server

        if build_inital_values:

            name = server.name.split('.')[0]

            self.fields["username"].initial = name
            self.fields["epfl_host"].initial = name + '.epfl.ch'
            self.fields['mail_dest'].initial = request.user.email
            self.fields['mysql_password'].initial = str(uuid.uuid4())
            self.fields['password'].initial = str(uuid.uuid4())
            

class SetupAgepVMForCom(_Wizard):
    """Agep's Wizard for VMs."""

    _name = 'SetupAgepVMForCom'
    _description = 'Wizard to setup a new VM for a commision: Add user, setup apache and php, add x.epfl.ch entry, setup database and send confirmation email.'

    _nb_step = 2
    _nb_task = 11

    _steps_names = ['Server selection', 'Details confirmation']
    _tasks_names = ['Create user', 'Set password', 'Copy config scripts', 'Add user to the server', 'Create ssh folder', 'Update keymanager', 'Run keymanager', 'Create hostforwarding entry', 'Setup apache, php and cie', 'Setup mysql database', 'Send confirmation email']

    def display_step_1(self, request):

        if request.method == 'POST':
            form = Step1Form(request.POST)
        else:
            form = Step1Form()

        return ('', form, "$('#id_server').css('width', '220px').select2();")

    def save_step_1(self, form):
        server_pk = form.cleaned_data['server'].pk

        return {'server_pk': server_pk}

    def display_step_2(self, request):

        server = Server.objects.get(pk=self.step_data[0]['server_pk'])

        if request.method == 'POST':
            form = Step2Form(server, False, request, request.POST)
        else:
            form = Step2Form(server, True, request)

        return ('If needed, you can edit values of this forms. You can leave them to defaults values, everything should be ok !', form, "$('#id_template').css('width', '220px').select2();")

    def save_step_2(self, form):
        return form.cleaned_data

    def do_task_1(self):
        """Create the user"""

        server = Server.objects.get(pk=self.step_data[0]['server_pk'])

        os.system('ssh ' + server.ssh_connection_string_from_gestion + ' useradd -s /bin/zsh -m ' + self.step_data[1]['username'])

        return (True, None)

    def do_task_2(self):
        """Set the user password"""

        server = Server.objects.get(pk=self.step_data[0]['server_pk'])

        if self.step_data[1]['password'] != '':
            os.system('ssh ' + server.ssh_connection_string_from_gestion + ' "echo \'' + self.step_data[1]['username'] + ':' + self.step_data[1]['password'] + '\' | chpasswd"')

        return (True, None)

    def do_task_3(self):
        """Copy config scripts"""

        server = Server.objects.get(pk=self.step_data[0]['server_pk'])

        t = Task(creation_date=timezone.now(), server=server, command=settings.COPY_USER_CONFIG_FABRIC_SCRIPT, args=self.step_data[1]['username'])
        t.save()
        run_task(t.pk)

        return (True, None)

    def do_task_4(self):
        """Add user to the server"""

        server = Server.objects.get(pk=self.step_data[0]['server_pk'])

        ServerUser(server=server, name=self.step_data[1]['username']).save()

        return (True, None)

    def do_task_5(self):
        """Create the SSH folder"""

        server = Server.objects.get(pk=self.step_data[0]['server_pk'])

        os.system('ssh ' + server.ssh_connection_string_from_gestion + ' "mkdir ~' + self.step_data[1]['username'] + '/.ssh/"')
        os.system('ssh ' + server.ssh_connection_string_from_gestion + ' "chown ' + self.step_data[1]['username'] + ' ~' + self.step_data[1]['username'] + '/.ssh/"')

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

    def do_task_8(self):
        """Add the new entry for hostforwarding"""

        server = Server.objects.get(pk=self.step_data[0]['server_pk'])

        if self.step_data[1]['create_epfl_host']:

            if settings.NGNIX_SSL_KEY != '':
                Hostnameforwarded(server_host=server.vm_host, server_to=server, domain=self.step_data[1]['epfl_host'], port_from=443).save()

            Hostnameforwarded(server_host=server.vm_host, server_to=server, domain=self.step_data[1]['epfl_host']).save()
            update_hostnameforwarding()

        return (True, None)

    def do_task_9(self):
        """Run the fabric script to setup the server with apache and cie"""

        server = Server.objects.get(pk=self.step_data[0]['server_pk'])

        t = Task(creation_date=timezone.now(), server=server, command='agep.setup_agep_vm')

        data = {'user': self.step_data[1]['username'], 'sudo': 'False'}
        if self.step_data[1]['grant_sudo_rights']:
            data['sudo'] = 'True'
        import json
        t.args = json.dumps(data)

        t.save()
        run_task(t.pk)


        return (True, None)

    def do_task_10(self):
        """Run the fabric script to setup mysql, if needed"""

        server = Server.objects.get(name=settings.MYSQL_VM)

        if self.step_data[1]['create_mysql_database']:

            t = Task(creation_date=timezone.now(), server=server, command='agep.setup_mysql')

            data = {'user': self.step_data[1]['username'], 'password': self.step_data[1]['mysql_password']}
            import json
            t.args = json.dumps(data)

            t.save()
            run_task(t.pk)


        return (True, None)

    def do_task_11(self):
        """Run the fabric script to setup mysql, if needed"""

        server = Server.objects.get(pk=self.step_data[0]['server_pk'])

        if self.step_data[1]['send_confirmation_email'] and self.step_data[1]['mail_dest']:

            bdd = ''
            sudo = ''

            if self.step_data[1]['create_mysql_database']:
                bdd = 'Les parametres d\'access a la base de donnee sont:\nUsername: ' + self.step_data[1]['username'] + '\nMot de passe: ' + self.step_data[1]['mysql_password'] + '\nHost: mysql\nDatabase: ' + self.step_data[1]['username'] + '\n\n'
            if self.step_data[1]['grant_sudo_rights']:
                sudo = 'L\'utilisateur dispose des droits sudo. Merci de ne pas supprimer les cles SSH de root ou la VM sera potentiellement detruite automatiquement. Usage a vos risques et perils !\n\n'
            
            send_mail('[Azimut-gestion::AgepolySetupScript] Parametres pour ' + server.name, 'Bonjour !\n\nJe suis le script de deployment pour l\'AGEPoly et j\'ai le bonheur de vous annonce que j\'ai fini mon travail :]\n\nLes parametres pour la machine ' + server.name + ' sont les suivants:\n\nConnection ssh: ssh ' + server.ssh_connection_string_from_backup.replace('root@', '') + '\nUsername: ' + self.step_data[1]['username'] + '\nMot de passe: ' + self.step_data[1]['password'] + '\n\nLes fichiers web sont a mettre dans le dossier ~/public_html/, les logs sont dans ~/logs/.\n\n' + bdd + sudo + 'Joyeuse journee,\nLe script\n\nPs: N\'oubliez jamais de faire des backups ;)', 'nobody@agepoly.ch',  self.step_data[1]['mail_dest'].split(','), fail_silently=False)


        return (True, None)

