azimut-gestion
==============

azimut-gestion is a small tool to manage an architecture of servers, using proxmox.


azimut-gestion use fabric scripts for deployement, who can be found [here](https://github.com/Azimut-Prod/azimut-deploy).

The tool is written in python and use :

* django
* fabric
* requests
* pyproxmox
* celery
* select2
* [Bootstrap-Admin-Theme](https://github.com/VinceG/Bootstrap-Admin-Theme)
* ZeroClipBoard
* south

Main features are:

* Proxmox containers management
* SSH key deployement
* Port forwarding from proxmox hosts to containers
* HTTP requests forwarding to containers usings ngnix
* Backups management
* Samba shares management
* Automatic deployement of new containers
* Execution of fabric scripts

Everything is put under MIT license.

Documents about each modules and setup can be found inside the [doc](doc/) folder.