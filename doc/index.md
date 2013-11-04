azimut-gestion - index
======================

## General

azimut-gestion is composed of multiples modules, for different tasks. A main module is the server module, taking care of saving all information about different servers and proxmox containers.

The system use celery to execute long task - avoid the HTTP interface to be blocked until the end of a complex task (e.g. deployment of a virtual machine).

The creation of a new server can be complex: creation of the server, deployment of the container, setup of backups, etc. To simply tasks, it's possible to create and run wizards, taking care of everything for a task.

## Architecture

<Schema should be put here>

### Core

The `gestion` server or proxmox container is the core of the interface. He takes connect to others servers to execute tasks (e.g. backups, deployments, update of configurations for services). The interface and the database is on this server, as the rabbitmq server and the celery daemon, taking care of executing background tasks. The `gestion` server must be able to access to every machine he as to manage using ssh.

### Backups

To execute backups, `rsnapshot` and `rsync` is used to create a copy of the server, with differents snapshot (copied each 4 hours, with history of 6 copy, last 7 days each day, last 4 week each week and last 3 months each month). The `gestion` server will connect to the backup server to execute rsync tasks, connecting themselves to different servers to backups. Therefor, the backup server must be able to connect using ssh to every machine who has to be backuped.

### Key management

For the deployment of ssh keys, a cron task is used to update the `authorized_keys2` file with keys. As keys are retrieved from the gestion server, and to avoid attacks or unwanted keys, servers *should access the gestion server via a secure connection*. Use HTTPS or disable the keymananger, otherwise **your servers may be at risk** !

## The server module

The server module is taking care of storing all needed information on different servers, virtual machines or proxmox containers. The different settings are:

### Name

The name of the server. This should be the domain name of the machine.

### Keymanager name

The name used for the keymanager script. This can be different from the name or the server and doesn't have to be unique.

### Is vm

Check this if the server is a virtual machine or a proxmox container

### External ip

The public ip of the server (can be a local ip). Don't fill this field if the server is a virtual machine or a proxmox containers connected only to the internal proxmox network.

### Internal ip

The ip of the virtual machine or proxmonx container on the internal proxmox network.

### Vm host

For a virtual machine or a proxmox container, the host server.

### Ngnix server

For a proxmox server, the virtual machine or proxmox container taking care of forwarding HTTP requests to other virtual machine with ngnix.

### Ssh connection string from gestion

The ssh connection string to use to connect to the server from the gestion server. If a special port is needed, use the following syntax: `-p 222 root@server.ch`.

If the server is a proxmox container on the same proxmox host than the gestion server, this field should look like `root@<internalhostip>`.

If the server is a proxmox container on another proxmox host than the gestion server, this field should look like `-p <sshportforwardedtovm> root@<externalhostip>`

In other cases, this filed should look like `root@<serverip>`

### Ssh connection string from backup

Like the previous filed, but for connections from the backup server. Use the same logic !

### External interface

For a proxmox server, the main external interface. THis is usually `vmbr0`, but for some special installs it's `eth0`.

### Is proxmox

Check this check-box if this is a proxmox server.

### Proxmox node name

The name of the proxmox node, in case of a proxmox server.

### External hostname for vms creation

The external hostname for creation of proxmox containers using the wizard. If not set, the name of the server will be used. This is usefull if you have a special dns for a local proxmox server, allowing him to be reached outside your LAN network.

### Samba management

Check this check box if you want to manage the samba service of this server.

### Samba base folder

The base folder to use for shares of the samba server.

### Users

The list of users on the server. Used by the keymanager. `root` should be in this list.


### Server details

If you click on a server, you will display details on the server and shortcuts to different features of others modules. Check the description of others modules for details !

## The users module

The users modules let you manage the list of users allowed to use the interface. If you create a new user, `don't forget to set his password` on the user details pages, otherwise he won't be able to login.

A user must be an admin to use the interface, but he will always be able to manage his own ssh keys. Details about ssh keys later, in the keymanager module.

## The group module

You can specify different groups to manage copy of different ssh keys to different servers. We recommend you to create a `Gestion` group, with the ssh key of the gestion server and your different backups servers, a `Users` groups, to include all users of your system, and a `Server` group, for all your servers.

A group can have different members: there is a list of users, a list of servers and a list of servers keys who are in the group. When a server is in a group, all his ssh keys are used. If an user is in a group, all his ssh keys are in a group. And at least, all specific servers ssh keys are in the group.

A group is allowed to connect to different servers: there is a list of servers, providing access to all users of the server, and a list of server user, allowing access only to the specified users on a server. 

Based on this rules (list of ssh keys of users and servers in the groups), the `authorized_keys2` of different servers users is build, taking the keys of groups allowed to connect to different users accounts.

## The keymanager module

The keymanger module take care of creating `authorized_keys2` files based on rules described for the group module. You can display a summary for different users and servers on the keymanager page, and the script to use to update the `authorized_keys2` file of a server, for all users. You can setup the script yourself, but there is a fabric task who can do it for you.

The keys are updated each hours, using a cron task, if you use the fabric script.

* Never use this system is the connection to the gestion server is not secure (e.g. not HTTPS): someone may be able to send and update unwanted ssh keys and connect to your server ! *

## The portfowarding module

The proxmox server, if configured, can forward connections of specific ports to a virtual machine or a proxmox container. For example, he may forward all connections to the port 80 to the ngnix server who will take care of HTTP requests.

The gestion server copy a script, `/etc/init.d/nat-vz`, who update the nat table of iptables as configured on the system. He also allow and forward connections from virtual machines and proxmox containers to the external network.

You can add rules in the portforwarding menu, specify the host server (the proxmox server), the server who will get the connection, the source port, the destination port and the protocol. You cannot forward a source port on the same host to different servers !

You can also display and add or remove rules on a server details page. Server host or destination will be filled for you and not displayed.

Every change is applied immediately, using a celery task. *Be careful and don't remove needed rules*, e.g to your ngnix server !

## The hostnameforwarding module

This module allows you to forward http requests on a specific domain to another server. Ngnix is used as proxy, and should be on a special vm of your proxmox server.

The gestion server generate the ngnix config (`/etc/nginx/sites-available/ngnix.conf`) and copy it to the ngnix server. If you setuped the ngnix server yourself, don't forget to enable the configuration (`ln -s /etc/nginx/sites-available/ngnix.conf /etc/nginx/sites-enabled/ngnix.conf`).

You can add rules in the hostnameforwarding menu, specifying the host server (the proxmox server), the destination server, the source port and the destination port. If you use a special source port, don't forget you may have to forward the port to the ngnix server using the portforwarding module !

You can also display and add or remove rules on a server details page. Server host or destination will be filled for you and not displayed.

Every change is applied immediately, using a celery task. *Be careful and don't remove needed rules*, e.g to your gestion server !

## The backup module

The point of this module is to backup your servers. `rsync` is used, to create a copy of your data, using a cron job and celery tasks. You can run a backup manually, and result of backups are shown on the dashboard, the backup menu and on the server details pages. If all texts are green, everything should be ok.

You can specify the source server and folder, the destination server and folder, and if you want to exclude some folders. You can use the checkbox to exclude /proc and /sys.

The exclude list is a comma separated list, relative to the source folder. If you want to exclude the folder `/the/game` when backuping `/`, use `/the/game`. If you backup `/the/`, usegit_hook `/game`.

*Careful ! If you remove a file on a server, the backup will also remove it !*

*Careful ! When you setup backups, use only dedicated empty destinations folders ! `rsync` will erase existing files on the destination !*

To setup the cron job, create a task running the django command `python manage.py backup_cron` when you want to execute your backups. Only actives backup will be done using this command.

You can display the results of backups on the details page of a backup, showing errors if something went wrong. The total size of a backup is also displayed, if the size is 0 you may have a problem.

The backup server is the one establishing the connection, using ssh to the server to be backuped. Be sure he can, using the keymanager or manually copying ssh keys.

*Always tests your backups. Never trust a backup system and be ready for anything. Watch your backup system.*

## The proxmox module

This module connect to proxmox server and display the list of running openvz containers. He will try to match the list using the list of servers, and let you create a new container if a server doesn't exists. You can also stop, start and edit configuration of containers. No restart is needed we you change a parameters of an openvz container !

To be able to work, the module use the proxmox API and an user, using settings `PROXMOX_USER` and `PROXMOX_PASS`. You have to set the full username, e.g. for a pam user, `api@pam`.

Virtual machines created use a generated, deterministic but hard-to-guess root passwords. Scripts are able to use this passwords for execution (e.g. to setup the keymanager) and they are not displayed to the users. They are generated from the `VM_PASS_SECRET` setting.

## The samba module

The samba module allow you to create shares, associated with one user and one password. This module is useful to provide network shares to windows machines for backups. 
Passwords are generated using the setting `SAMBA_SECRET_KEY`. Users are created on the system, using the setting `SAMBA_USER_PREFIX`, with a disabled shell. Keep in mind those users may still be able to uses some resources (e.g.: samba shares ;) ).

Path are prefixed with the setting set on the server module, allowing you to restrict folders shared. The module is not able to let more than one user access the same share nor folder.

The module save config in the file `/etc/smb.shares.conf`. You have to specify in the main samba configuration file to include this one.

## The fabrun module

This module run fabric scripts on your servers, using the folder `FABRIC_FOLDER` in settings. Output is displayed after a run, including stderr.

In the docstring of fabric function, it's possible to use special string to tell the module some environment variables to be set. Those should be used for internal use, but you may need them:

### [$AG:NeedGestion]

If the current server is on the same host than the gestion server (as set in settings), set `gestion_ip` to the internal gestion server ip and `gestion_name` to the gestion server hostname.

Settings are `GESTION_IP` (the ip of the gestion server), `GESTION_NAME` (the name of the gestion server) and `GESTION_VM_NAME` (the name of the proxmox server with the gestion server).

Internal machines cannot access the gestion server using external ip and this is used to optionally add an entry into the `/etc/hosts` file to ensure access.

### [$AG:NeedKM]

Set `keymanagerName` to the keymanager name of the current server and `keyManagerUsers` to the list of users of the server.

### [$AG:NeedUser]

Internal use. Set `fab_user` from the task arguments.

## The wizard module

The wizard module allow a set of tasks to be executed. There is two phases of a wizard: the setup phase, using different step, asking user for informations and the execution phase, executing different tasks the wizard have to do.

Tasks are executed using celery and you can watch the progress.

### Included wizards

#### Create_user

Add a new user on a server, updating the keymanager and the server.

#### Create_vm

Let you setup and deploy a new server. You have to set the name and the proxmox host and all others parameters are computed for you. You can then edit parameters and disable parts of the wizard if needed. Then:

* The server is created in the server module
* The server is added to the defaults groups (`CREATEVM_DEFAULT_GROUPS`)
* Default groups are allowed to connect to the server (`CREATEVM_DEFAULT_GROUPS_ALLOWED)
* The container is created on the proxmox server
* SSH port is forwarded to the server
* Domain is forwarded to the server
* The setup fabric script is executed (`SETUP_FABRIC_SCRIPT`)
* A backup task is created and executed (Using `BACKUP_SERVER` and `BACKUP_BASE_FOLDER`)


### Your own wizards

Wizard are python class, and stored inside the `wizard/wizards` folder. If you want to implement a new wizard, you need to create a new class, extending `_Wizard` and set the following parameters:

#### _name
The name of your wizard
#### _description
The description of your wizard
#### _nb_step
THe number of setup step for your wizard
#### _nb_task
The number of tasks for your wizard
#### _steps_names
A list of name for steps of the wizard
#### _tasks_names
A list of name for steps of the wizard

Then you have to create 

*`display_step_x`, with x = 1 -> number of step, taking a django request as parameter and returning (A bonus text, A form, Some extra javascript), to display a wizard step
*`save_step_x`, with x = 1 -> number of step, taking the valid from from `display_step_x` and returning a dict of data to save (data must be serializable)
*`do_task_x`, with x = 1 -> number of tasks, taking no arguments and returning (True, dict of data to save) if the wizard should continue or (False, None) otherwise.

Data from step is saved in `self.step_data[step_id-1]` and tasks in `self.task_data[step_id-1]`.

You can check implementation of defaults wizards for examples.

## Git hooks

As the system use some git repository (e.g. for fabric script), it's possible to update them using hooks.

Using the setting `GIT_REPOS` you can specify a dict of key: path. If you access gestionurl/git_hook/key/, the server will do a git pull on the path to update the repository.

## Misc

`GESTION_URL` setting have to be set to the full url to access the gestion server.