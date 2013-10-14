# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Backup'
        db.create_table(u'backups_backup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('server_from', self.gf('django.db.models.fields.related.ForeignKey')(related_name='backups_of_the_server', to=orm['servers.Server'])),
            ('server_dest', self.gf('django.db.models.fields.related.ForeignKey')(related_name='backups_on_the_server', to=orm['servers.Server'])),
            ('folder_from', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('folder_to', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('prox_and_sys_excludes', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('excludes', self.gf('django.db.models.fields.TextField')()),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'backups', ['Backup'])

        # Adding model 'BackupRun'
        db.create_table(u'backups_backuprun', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('backup', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['backups.Backup'])),
            ('start_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('size', self.gf('django.db.models.fields.BigIntegerField')()),
            ('nb_files', self.gf('django.db.models.fields.BigIntegerField')()),
        ))
        db.send_create_signal(u'backups', ['BackupRun'])


    def backwards(self, orm):
        # Deleting model 'Backup'
        db.delete_table(u'backups_backup')

        # Deleting model 'BackupRun'
        db.delete_table(u'backups_backuprun')


    models = {
        u'backups.backup': {
            'Meta': {'object_name': 'Backup'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'excludes': ('django.db.models.fields.TextField', [], {}),
            'folder_from': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'folder_to': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'prox_and_sys_excludes': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'server_dest': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'backups_on_the_server'", 'to': u"orm['servers.Server']"}),
            'server_from': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'backups_of_the_server'", 'to': u"orm['servers.Server']"})
        },
        u'backups.backuprun': {
            'Meta': {'object_name': 'BackupRun'},
            'backup': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['backups.Backup']"}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nb_files': ('django.db.models.fields.BigIntegerField', [], {}),
            'size': ('django.db.models.fields.BigIntegerField', [], {}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'servers.server': {
            'Meta': {'object_name': 'Server'},
            'external_interface': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'external_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'is_vm': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'keymanger_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ngnix_server': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ngnixed_server_set'", 'null': 'True', 'to': u"orm['servers.Server']"}),
            'ssh_connection_string_from_backup': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'ssh_connection_string_from_gestion': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'vm_host': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'server_set'", 'null': 'True', 'to': u"orm['servers.Server']"})
        }
    }

    complete_apps = ['backups']