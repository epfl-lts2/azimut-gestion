azimut-gestion - setup
======================

This file describe how to setup azimut-gestion.

We assume you have:

* A proxmox host : myproxmox.domain.com - 192.168.1.42
* A backup host : backups.domain.com - 192.168.1.99
    *.myproxmox.domain.com as a CNAME to myproxmox.domain.com
    * If you don't have the hostname set, the setup script will fail !
* Fabric installed, with pyproxmox


## Proxmox setup

To install proxmox, just follow [the official guide](http://www.proxmox.com/proxmox-ve/get-started)

We created a fabric script who is going to setup everything on the proxmox host. He will:

* Setup proxmox server
    * Upgrade the proxmox server
    * Add a user for the gestion vm, with admin rights
    * Setup networking
        * With basic port forwarding
* Create the nginx container
    * Setup ngnix
* Create the gestion container
    * Setup apache
    * Setup rabbitmq
    * Install python and dependencies
    * Install mysql
    * Clone repositories
    * Configure the gestion tool
    * Add defaults servers (the proxmox server, nginx and gestion VM)
* Execute setup script on defaults servers
    * Install default tools and configuration
    * Copying SSH keys

Be careful ! Some passwords may appear in the output logs or can been seen using `ps aux`.

A rabbitmq `admin` user and a mysql `root` user will be created using the root password provided.

Unprivileged accounts are created using random passwords for services. This include the user to connect to rabbitmq, mysql and the proxmox API.

Default VMs password is random. You should use ssh keys to access new VMs. Gestion and ngnix VMs, setuped by the main script will have the root password provided.

The proxmox machine will be restarted during installation.

To do the installation:

* Clone the azimut-deploy repository
    * `git clone git@github.com:Azimut-Prod/azimut-deploy.git`
* Clone the azimut-config repositroy
    * `git clone git@github.com:Azimut-Prod/azimut-config.git`
* Configure azimut-deploy
    * `cd azimut-deploy`
    * `cp config.py.dist config.py`
    * If needed, edit config.py. You should at lease specify the gestion hostname (gestion.myproxmox.domain.com)
* Execute the fabric script
        * `fab gestion.setup_proxmox`. The script will ask you at the beginning for all informations he needs.

## Settings

Settings are set in the `settingsLocal.py` file, located in `/var/www/git-repo/azimut-gestion/app/` folder. The setup script generated one for you but you can always edit it. Details of settings can be found in the general documentation or in this document.

## Gestion setup

To finish the installation, just go you `http://gestion.myproxmox.domain.com`. You can use `admin` and the root password you provided during the setup script to login.

You can go to _Users_ to add new users or edit the `admìn` user. You can also add your ssh keys to be able to connect to VMs created.

If needed, you can change defaults groups created during installations. All users should be in the `People` groups and servers inside the `Servers` groups. Don't forget to edit your groups configuration in your `settingsLocal.py` to allow the _CreateVm_ wizard to add created VMs to the corrects groups.

### Backup server

It's important to do backups ! You should have an external server, able to connect to the proxmox servers and his VMs to perform backup.

The server should have `rsync` and `rsnapshot` tool installed.

Add the machine in the _Servers_ menu, with corrects parameters. You have too generate an ssh-key (`ssh-keygen`) for the root user. Attach it to the servers, and add this key (or the server) to the _Server gestion_  group. Don't forget to also allow the _Server gestion_ to connect to the server.

You can then execute the fabric script to setup the server using `fab server.setup`. The script will ask your for the keymanager name your set in the interface and the keymanager users (probably 'root' only).

Finally, you can set the server name and the base folder to do backups in your `settingsLocal.py` for the _CreateVM_ wizard. You can also add manually backups using the _Backups_ menu.

*Be careful when you set a backup destination !* Using / will erase your backup server, always your empty folders !

You must add cron jobs on the gestion machine to execute tasks. Add this:

`00 */4 * * * cd /var/www/git-repo/azimut-gestion && python manage.py backup_cron hourly`
`50 23 * * * cd /var/www/git-repo/azimut-gestion && python manage.py backup_cron daily`
`40 23 1,8,15,22 * * cd /var/www/git-repo/azimut-gestion && python manage.py backup_cron weekly`
`30 23 1 * * cd /var/www/git-repo/azimut-gestion && python manage.py backup_cron monthly`


## Update the code

It's possible to use the fabric script to update the code. Just use `fab gestion.update_code` to do it. Don't forget to check if your settings files are up-to-date ! (`/var/www/git-repo/azimut-gestion/app/settingsLocal.py` and `/var/www/git-repo/azimut-deploy/config.py`).

## SSL with ngnix

When the port 443 is used for hostforwarding and the config option `NGNIX_SSL_PEM` and `NGNIX_SSL_KEY` is set, ngnix config will be set to use SSL using the two files provided in config.

You may generate certificates like this:

* Login on the ngnix machine
* `mkdir -p /etc/ssl/ngnix`
* `cd /etc/ssl/ngnix`
* `openssl req -new -x509 -days 3650 -nodes -out /etc/ssl/ngnix/srv.pem -keyout /etc/ssl/ngnix/srv.key`

Update `settingsLocal.py`:

`NGNIX_SSL_PEM = '/etc/ssl/ngnix/srv.pem'`
`NGNIX_SSL_KEY = '/etc/ssl/ngnix/srv.key'`

Add a portforwarding entry to your ngnix server, from port 443 to port 443.

You can now add hostnameforwarding entry from the port 443 to your server (using port 80 as destination !).

## Zabbix

To monitor backups with zabbix, add this to one of your zabbix agent
`UserParameter=azimutgestion.[*],wget http://GESTION_HOST/backups/zabbix/$1/$2 -O - -o /dev/null`

and use the zabbix template 'Azmiut-gestion: Backups'

# Bind

To use the bind system, you need to install bind:

`apt-get install bind9`

Edit `/etc/bind/named.conf`, add `include "/etc/bind/named.conf.gestion";`

Edit your settingsLocal.py, add `DNS_SECRET = 'ASecret'`

At this point the bind server won't work. Use the gestion interface and add it as a bind server, then publish a first zone :)


