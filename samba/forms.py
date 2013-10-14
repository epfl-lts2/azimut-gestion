from django.forms import ModelForm

from samba.models import Share

from servers.models import Server


class ShareForm(ModelForm):
    class Meta:
        model = Share
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(ShareForm, self).__init__(*args, **kwargs)

        self.fields["server"].queryset = Server.objects.order_by('name').filter(samba_management=True)
