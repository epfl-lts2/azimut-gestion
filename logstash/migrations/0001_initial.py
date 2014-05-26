# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'File'
        db.create_table(u'logstash_file', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('server', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servers.Server'])),
            ('file', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('tags', self.gf('django.db.models.fields.CharField')(max_length=512)),
        ))
        db.send_create_signal(u'logstash', ['File'])


    def backwards(self, orm):
        # Deleting model 'File'
        db.delete_table(u'logstash_file')


    models = {
        u'logstash.file': {
            'Meta': {'object_name': 'File'},
            'file': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['servers.Server']"}),
            'tags': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'servers.server': {
            'Meta': {'object_name': 'Server'},
            'external_hostname_for_vms_creation': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'external_interface': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'external_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'hostname_for_vms_creation': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'is_proxmox': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_vm': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'keymanger_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'logstash_shipper': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ngnix_server': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ngnixed_server_set'", 'null': 'True', 'to': u"orm['servers.Server']"}),
            'proxmox_node_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'samba_base_folder': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'samba_management': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ssh_connection_string_from_backup': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'ssh_connection_string_from_gestion': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'vm_host': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'server_set'", 'null': 'True', 'to': u"orm['servers.Server']"})
        }
    }

    complete_apps = ['logstash']