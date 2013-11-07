from django.forms import ModelForm

from django.contrib.auth.models import User
from main.models import SshKey


class UserForm(ModelForm):
    class Meta:
        model = User
        exclude = ('password', 'last_login', 'is_superuser', 'date_joined', 'groups', 'user_permissions')


class UserOwnForm(ModelForm):
    class Meta:
        model = User
        exclude = ('password', 'last_login', 'is_superuser', 'date_joined', 'groups', 'user_permissions', 'is_staff', 'username', 'is_active')


class UserSshKey(ModelForm):
    class Meta:
        model = SshKey
        exclude = ('user',)


class SshKeyForm(ModelForm):
    class Meta:
        model = SshKey

    def __init__(self, *args, **kwargs):
        super(SshKeyForm, self).__init__(*args, **kwargs)
        self.fields["user"].queryset = User.objects.order_by('username')
