from django.forms import ModelForm

from backups.models import Backup

from servers.models import Server


class BackupForm(ModelForm):
    class Meta:
        model = Backup
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(BackupForm, self).__init__(*args, **kwargs)
        self.fields["server_from"].queryset = Server.objects.order_by('name')
        self.fields["server_to"].queryset = Server.objects.order_by('name')
