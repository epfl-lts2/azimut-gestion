from django.forms import ModelForm

from servers.models import Server, SshKey


class ServerForm(ModelForm):
    class Meta:
        model = Server
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(ServerForm, self).__init__(*args, **kwargs)
        self.fields["vm_host"].queryset = Server.objects.filter(is_vm=False).order_by('name').exclude(pk=kwargs['instance'].pk)
        self.fields["ngnix_server"].queryset = Server.objects.filter(is_vm=True).order_by('name').filter(vm_host=kwargs['instance'])


class ServerSshKey(ModelForm):
    class Meta:
        model = SshKey
        exclude = ('server')


class SshKeyForm(ModelForm):
    class Meta:
        model = SshKey

    def __init__(self, *args, **kwargs):
        super(SshKeyForm, self).__init__(*args, **kwargs)
        self.fields["server"].queryset = Server.objects.order_by('name')
