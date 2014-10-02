from django.forms import ModelForm

from dnsgestion.models import Zone, Entry
from servers.models import Server


class ZoneForm(ModelForm):
    class Meta:
        model = Zone
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(ZoneForm, self).__init__(*args, **kwargs)

        self.fields["server"].queryset = Server.objects.filter(bind_server=True).order_by('name')


class EntryForm(ModelForm):
    class Meta:
        model = Entry
        exclude = ('zone', 'order')
