# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Hostnameforwarded.port_from'
        db.add_column(u'hostnameforwarding_hostnameforwarded', 'port_from',
                      self.gf('django.db.models.fields.IntegerField')(default=80),
                      keep_default=False)

        # Adding field 'Hostnameforwarded.port_to'
        db.add_column(u'hostnameforwarding_hostnameforwarded', 'port_to',
                      self.gf('django.db.models.fields.IntegerField')(default=80),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Hostnameforwarded.port_from'
        db.delete_column(u'hostnameforwarding_hostnameforwarded', 'port_from')

        # Deleting field 'Hostnameforwarded.port_to'
        db.delete_column(u'hostnameforwarding_hostnameforwarded', 'port_to')


    models = {
        u'hostnameforwarding.hostnameforwarded': {
            'Meta': {'object_name': 'Hostnameforwarded'},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'port_from': ('django.db.models.fields.IntegerField', [], {'default': '80'}),
            'port_to': ('django.db.models.fields.IntegerField', [], {'default': '80'}),
            'server_host': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'hoststoforward'", 'to': u"orm['servers.Server']"}),
            'server_to': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'hostforwarded'", 'to': u"orm['servers.Server']"})
        },
        u'servers.server': {
            'Meta': {'object_name': 'Server'},
            'external_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'is_vm': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'keymanger_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ssh_connection_string': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'vm_host': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['servers.Server']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['hostnameforwarding']