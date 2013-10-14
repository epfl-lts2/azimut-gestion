from django.forms import ModelForm

from hostnameforwarding.models import Hostnameforwarded

from servers.models import Server


class HostnameforwardedForm(ModelForm):
    class Meta:
        model = Hostnameforwarded
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(HostnameforwardedForm, self).__init__(*args, **kwargs)

        self.fields["server_host"].queryset = Server.objects.order_by('name').filter(is_vm=False)
        self.fields["server_to"].queryset = Server.objects.order_by('name').filter(is_vm=True)
