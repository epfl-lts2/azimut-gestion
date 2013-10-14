from django.forms import ModelForm

from portforwarding.models import Portforwarded

from servers.models import Server


class PortforwardedForm(ModelForm):
    class Meta:
        model = Portforwarded
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(PortforwardedForm, self).__init__(*args, **kwargs)

        self.fields["server_host"].queryset = Server.objects.order_by('name').filter(is_vm=False)
        self.fields["server_to"].queryset = Server.objects.order_by('name').filter(is_vm=True)
