from django.db import models


class Execution(models.Model):

    current_task = models.IntegerField()
    done = models.BooleanField()
