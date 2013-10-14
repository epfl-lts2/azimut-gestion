from celery import task

from django.conf import settings
import os


@task(ignore_result=True)
def update_git_repo(id):
    """Update a git repository"""

    if id not in settings.GIT_REPOS:
        print "Error, not git with id", id
        return

    os.system("cd " + settings.GIT_REPOS[id] + " && git pull")
