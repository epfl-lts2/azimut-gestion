# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Execution'
        db.create_table(u'wizard_execution', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('current_task', self.gf('django.db.models.fields.IntegerField')()),
            ('done', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'wizard', ['Execution'])


    def backwards(self, orm):
        # Deleting model 'Execution'
        db.delete_table(u'wizard_execution')


    models = {
        u'wizard.execution': {
            'Meta': {'object_name': 'Execution'},
            'current_task': ('django.db.models.fields.IntegerField', [], {}),
            'done': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['wizard']