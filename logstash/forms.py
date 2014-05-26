from django.forms import ModelForm

from logstash.models import File

from servers.models import Server


class FileForm(ModelForm):
    class Meta:
        model = File
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(FileForm, self).__init__(*args, **kwargs)

        self.fields["server"].queryset = Server.objects.order_by('name').filter(logstash_shipper=True)
