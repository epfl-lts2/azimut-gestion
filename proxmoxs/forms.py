from django import forms


class NewVMForm(forms.Form):
    ram = forms.IntegerField(help_text='Mb', initial="512", min_value=256)
    swap = forms.IntegerField(help_text='Mb', initial="512", min_value=0)
    disk = forms.IntegerField(help_text='Gb', initial="10", min_value=5)
    cpus = forms.IntegerField(initial="1", min_value=1)
    template = forms.ChoiceField()

    def __init__(self, choices, *args, **kwargs):
        super(NewVMForm, self).__init__(*args, **kwargs)
        self.fields['template'].choices = choices


class EditVMFOrm(forms.Form):
    ram = forms.IntegerField(help_text='Mb', initial="512", min_value=256)
    swap = forms.IntegerField(help_text='Mb', initial="512", min_value=0)
    disk = forms.IntegerField(help_text='Gb', initial="10", min_value=5)
    cpus = forms.IntegerField(initial="1", min_value=1)

    def __init__(self, disk, mem, swap, cpus, *args, **kwargs):
        super(EditVMFOrm, self).__init__(*args, **kwargs)

        self.fields['ram'].initial = mem
        self.fields['swap'].initial = swap
        self.fields['disk'].initial = disk
        self.fields['cpus'].initial = cpus
