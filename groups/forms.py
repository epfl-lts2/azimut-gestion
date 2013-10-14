from django.forms import ModelForm

from groups.models import Group
from django.contrib.auth.models import User
from servers.models import Server, SshKey, ServerUser


class GroupForm(ModelForm):
    class Meta:
        model = Group
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        self.fields["servers"].label = 'Servers (all users)'
        self.fields["servers_keys"].label = 'Servers (by users)'

        self.fields["servers"].queryset = Server.objects.order_by('name')
        self.fields["allowed_servers"].queryset = Server.objects.order_by('name')
        self.fields["servers_keys"].queryset = SshKey.objects.order_by('user', 'server__name')
        self.fields["users"].queryset = User.objects.order_by('username')
        self.fields["allowed_servers_users"].queryset = ServerUser.objects.order_by('name', 'server__name')
