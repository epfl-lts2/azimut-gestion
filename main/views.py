# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404, HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.utils.encoding import smart_str
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.db import connections
from django.core.paginator import InvalidPage, EmptyPage, Paginator
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.contrib import messages

from django.contrib.auth.models import User
from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm

from main.forms import UserForm, UserOwnForm, UserSshKey, SshKeyForm
from main.models import SshKey
from groups.models import Group
from main.tasks import update_git_repo
from backups.models import Backup, BackupSetOfRun
from servers.models import Server


def home_redirect(request):
    """Redirect the user to the home page, forcing HTTPs if needed. As the real home force authentification, this try to force https for the login too"""

    if not request.is_secure() and settings.FORCE_SECURE_FOR_USER:
        return HttpResponseRedirect('https://' + request.get_host() + request.path)

    r = redirect('main.views.home')
    if settings.FORCE_SECURE_FOR_USER:
        r['Strict-Transport-Security'] = 'max-age=31536000'
    return r


@login_required
def home(request):
    """Show the welcome page"""

    if not request.is_secure() and settings.FORCE_SECURE_FOR_USER:
        return HttpResponseRedirect('https://' + request.get_host() + request.path)

    backups = Backup.objects.order_by('name').all()

    last_hourlys = BackupSetOfRun.objects.order_by('-start_date').filter(type='hourly').all()
    last_daily = BackupSetOfRun.objects.order_by('-start_date').filter(type='daily').all()
    last_weekly = BackupSetOfRun.objects.order_by('-start_date').filter(type='weekly').all()
    last_monthly = BackupSetOfRun.objects.order_by('-start_date').filter(type='monthly').all()

    return render_to_response('main/home.html', {'backups': backups, 'last_daily': last_daily, 'last_weekly': last_weekly, 'last_hourlys': last_hourlys, 'last_monthly': last_monthly}, context_instance=RequestContext(request))


@login_required
def me(request):
    """Show the page about the current user"""

    return render_to_response('main/me.html', {}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def users_list(request):
    """Show the list of users"""

    liste = User.objects.order_by('username').all()

    return render_to_response('main/users/list.html', {'liste': liste}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def users_show(request, pk):
    """Show details of an user"""

    object = get_object_or_404(User, pk=pk)

    groups = Group.objects.exclude(users=object).order_by('name').all()
    servers = Server.objects.exclude(users_owning_the_server=object).order_by('name').all()

    return render_to_response('main/users/show.html', {'object': object, 'groups': groups, 'servers': servers}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def users_edit(request, pk):
    """Edit an user"""

    try:
        object = User.objects.get(pk=pk)
    except:
        object = User()

    if request.method == 'POST':  # If the form has been submitted...
        form = UserForm(request.POST, instance=object)

        if form.is_valid():  # If the form is valid
            object = form.save()

            messages.success(request, 'The user has been saved.')

            return redirect(reverse('main.views.users_list'))
    else:
        form = UserForm(instance=object)

    return render_to_response('main/users/edit.html', {'form': form}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def users_delete(request, pk):
    """Delete an user"""

    object = get_object_or_404(User, pk=pk)

    # Don't delete ourself
    if object.pk != request.user.pk:
        object.delete()

    messages.success(request, 'User has been deleted.')

    return redirect(reverse('main.views.users_list', args=()))


@login_required
@staff_member_required
def users_setpassword(request, pk):

    object = get_object_or_404(User, pk=pk)

    if request.method == 'POST':  # If the form has been submitted...
        form = AdminPasswordChangeForm(user=object, data=request.POST)

        if form.is_valid():  # If the form is valid
            form.save()

            messages.success(request, 'The password has been saved.')

            return redirect(reverse('main.views.users_show', args=(object.pk, )))
    else:
        form = AdminPasswordChangeForm(user=object)

    return render_to_response('main/users/setpassword.html', {'form': form}, context_instance=RequestContext(request))


@login_required
def me_password(request):
    """Form to change user password"""

    if request.method == 'POST':  # If the form has been submitted...
        form = PasswordChangeForm(user=request.user, data=request.POST)

        if form.is_valid():  # If the form is valid
            form.save()

            messages.success(request, 'The password has been saved.')

            return redirect(reverse('main.views.me',))
    else:
        form = PasswordChangeForm(user=request.user)

    return render_to_response('main/password.html', {'form': form}, context_instance=RequestContext(request))


@login_required
def me_edit(request):
    """Edit ourself"""

    if request.method == 'POST':  # If the form has been submitted...
        form = UserOwnForm(instance=request.user, data=request.POST)

        if form.is_valid():  # If the form is valid
            form.save()

            messages.success(request, 'Your profile has been saved.')

            return redirect(reverse('main.views.me',))
    else:
        form = UserOwnForm(instance=request.user)

    return render_to_response('main/me_edit.html', {'form': form}, context_instance=RequestContext(request))


@login_required
def users_keys_add(request, pk):
    """Add a key to the user"""

    if pk and request.user.is_staff:
        user = get_object_or_404(User, pk=pk)
    else:
        user = request.user

    baseKey = SshKey(user=user)

    if request.method == 'POST':  # If the form has been submitted...
        form = UserSshKey(instance=baseKey, data=request.POST)

        if form.is_valid():  # If the form is valid
            form.save()

            messages.success(request, 'The ssh key has been added.')

            if pk:
                return redirect(reverse('main.views.users_show', args=(pk, )))
            else:
                return redirect(reverse('main.views.me',))
    else:
        form = UserSshKey(instance=baseKey)

    return render_to_response('main/add_ssh.html', {'form': form, 'ownMode': not pk}, context_instance=RequestContext(request))


@login_required
def users_keys_delete(request, pk, keyPk):
    """Delete a key of the user"""

    if pk and request.user.is_staff:
        user = get_object_or_404(User, pk=pk)
    else:
        user = request.user

    baseKey = get_object_or_404(SshKey, user=user, pk=keyPk)

    baseKey.delete()

    messages.success(request, 'The ssh key has been deleted.')

    if pk:
        return redirect(reverse('main.views.users_show', args=(pk, )))
    else:
        return redirect(reverse('main.views.me',))


@login_required
@staff_member_required
def keys_list(request):
    """Show the list of keys"""

    liste = SshKey.objects.order_by('user__username').all()

    return render_to_response('main/keys/list.html', {'liste': liste}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def keys_show(request, pk):
    """Show details of an ssk key"""

    object = get_object_or_404(SshKey, pk=pk)

    return render_to_response('main/keys/show.html', {'object': object}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def keys_edit(request, pk):
    """Edit an ssh key"""

    try:
        object = SshKey.objects.get(pk=pk)
    except:
        object = SshKey()

    if request.method == 'POST':  # If the form has been submitted...
        form = SshKeyForm(request.POST, instance=object)

        if form.is_valid():  # If the form is valid
            object = form.save()

            messages.success(request, 'The ssh key has been saved.')

            return redirect(reverse('main.views.keys_list'))
    else:
        form = SshKeyForm(instance=object)

    return render_to_response('main/keys/edit.html', {'form': form}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def keys_delete(request, pk):
    """Delete an ssh key"""

    object = get_object_or_404(SshKey, pk=pk)

    object.delete()

    messages.success(request, 'The ssh key has been deleted.')

    return redirect(reverse('main.views.keys_list', args=()))


@login_required
@staff_member_required
def users_groups_add(request, pk):
    """Add a user to a group"""

    user = get_object_or_404(User, pk=pk)

    group = get_object_or_404(Group, pk=request.GET.get('groupPk'))

    group.users.add(user)

    messages.success(request, 'The user has been added to the group.')

    return redirect(reverse('main.views.users_show', args=(pk, )))


@login_required
@staff_member_required
def users_groups_delete(request, pk, groupPk):
    """Delete an user from a group"""

    user = get_object_or_404(User, pk=pk)

    group = get_object_or_404(Group, pk=groupPk)

    group.users.remove(user)

    messages.success(request, 'The user has been removed from the group.')

    return redirect(reverse('main.views.users_show', args=(pk, )))


@csrf_exempt
def git_hook(request, id):
    """Lanch a task to update a github repository"""

    update_git_repo.delay(id)

    return HttpResponse('Happy')


@login_required
@staff_member_required
def users_server_add(request, pk):
    """Add a user to a server access"""

    user = get_object_or_404(User, pk=pk)

    server = get_object_or_404(Server, pk=request.GET.get('serverPk'))

    server.users_owning_the_server.add(user)

    messages.success(request, 'The user has been added to the server.')

    return redirect(reverse('main.views.users_show', args=(pk, )))


@login_required
@staff_member_required
def users_server_delete(request, pk, serverPk):
    """Delete an user from a server access"""

    user = get_object_or_404(User, pk=pk)

    server = get_object_or_404(Server, pk=serverPk)

    server.users_owning_the_server.remove(user)

    messages.success(request, 'The user has been removed from the server.')

    return redirect(reverse('main.views.users_show', args=(pk, )))
