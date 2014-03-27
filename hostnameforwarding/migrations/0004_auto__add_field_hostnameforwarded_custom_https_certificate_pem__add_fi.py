# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Hostnameforwarded.custom_https_certificate_pem'
        db.add_column(u'hostnameforwarding_hostnameforwarded', 'custom_https_certificate_pem',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Hostnameforwarded.custom_https_certificate_key'
        db.add_column(u'hostnameforwarding_hostnameforwarded', 'custom_https_certificate_key',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Hostnameforwarded.custom_https_certificate_pem'
        db.delete_column(u'hostnameforwarding_hostnameforwarded', 'custom_https_certificate_pem')

        # Deleting field 'Hostnameforwarded.custom_https_certificate_key'
        db.delete_column(u'hostnameforwarding_hostnameforwarded', 'custom_https_certificate_key')


    models = {
        u'hostnameforwarding.hostnameforwarded': {
            'Meta': {'object_name': 'Hostnameforwarded'},
            'custom_https_certificate_key': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'custom_https_certificate_pem': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'force_https': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'port_from': ('django.db.models.fields.IntegerField', [], {'default': '80'}),
            'port_to': ('django.db.models.fields.IntegerField', [], {'default': '80'}),
            'server_host': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'hoststoforward'", 'to': u"orm['servers.Server']"}),
            'server_to': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'hostforwarded'", 'to': u"orm['servers.Server']"})
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

    complete_apps = ['hostnameforwarding']