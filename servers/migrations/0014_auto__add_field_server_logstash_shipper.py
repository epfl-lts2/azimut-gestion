# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Server.logstash_shipper'
        db.add_column(u'servers_server', 'logstash_shipper',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Server.logstash_shipper'
        db.delete_column(u'servers_server', 'logstash_shipper')


    models = {
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
        },
        u'servers.serveruser': {
            'Meta': {'object_name': 'ServerUser'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['servers.Server']"})
        },
        u'servers.sshkey': {
            'Meta': {'object_name': 'SshKey'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.TextField', [], {}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['servers.Server']"}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['servers']