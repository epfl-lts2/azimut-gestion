# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BackupSetOfRun'
        db.create_table(u'backups_backupsetofrun', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('start_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('total_size', self.gf('django.db.models.fields.BigIntegerField')()),
            ('total_files', self.gf('django.db.models.fields.BigIntegerField')()),
        ))
        db.send_create_signal(u'backups', ['BackupSetOfRun'])

        # Adding M2M table for field backups on 'BackupSetOfRun'
        m2m_table_name = db.shorten_name(u'backups_backupsetofrun_backups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('backupsetofrun', models.ForeignKey(orm[u'backups.backupsetofrun'], null=False)),
            ('backuprun', models.ForeignKey(orm[u'backups.backuprun'], null=False))
        ))
        db.create_unique(m2m_table_name, ['backupsetofrun_id', 'backuprun_id'])


    def backwards(self, orm):
        # Deleting model 'BackupSetOfRun'
        db.delete_table(u'backups_backupsetofrun')

        # Removing M2M table for field backups on 'BackupSetOfRun'
        db.delete_table(db.shorten_name(u'backups_backupsetofrun_backups'))


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'backups.backup': {
            'Meta': {'object_name': 'Backup'},
            'active': ('django.db.models.fields.BooleanField', [], {}),
            'excludes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'folder_from': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'folder_to': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'prox_and_sys_excludes': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'server_from': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'backups_of_the_server'", 'to': u"orm['servers.Server']"}),
            'server_to': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'backups_on_the_server'", 'to': u"orm['servers.Server']"})
        },
        u'backups.backuprun': {
            'Meta': {'object_name': 'BackupRun'},
            'backup': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['backups.Backup']"}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nb_files': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'size': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {}),
            'stderr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'stdout': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'backups.backupsetofrun': {
            'Meta': {'object_name': 'BackupSetOfRun'},
            'backups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['backups.BackupRun']", 'symmetrical': 'False'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'total_files': ('django.db.models.fields.BigIntegerField', [], {}),
            'total_size': ('django.db.models.fields.BigIntegerField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'servers.server': {
            'Meta': {'object_name': 'Server'},
            'external_hostname_for_vms_creation': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'external_interface': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'external_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'hostname_for_vms_creation': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'is_proxmox': ('django.db.models.fields.BooleanField', [], {}),
            'is_vm': ('django.db.models.fields.BooleanField', [], {}),
            'keymanger_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'logstash_shipper': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mysql_server': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'mysqled_server_set'", 'null': 'True', 'to': u"orm['servers.Server']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ngnix_server': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ngnixed_server_set'", 'null': 'True', 'to': u"orm['servers.Server']"}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'proxmox_node_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'samba_base_folder': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'samba_management': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ssh_connection_string_from_backup': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'ssh_connection_string_from_gestion': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'users_owning_the_server': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'vm_host': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'server_set'", 'null': 'True', 'to': u"orm['servers.Server']"})
        }
    }

    complete_apps = ['backups']