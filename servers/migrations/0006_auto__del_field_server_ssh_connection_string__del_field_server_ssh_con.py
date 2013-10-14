# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Server.ssh_connection_string'
        db.delete_column(u'servers_server', 'ssh_connection_string')

        # Deleting field 'Server.ssh_connection_string_for_ngnix'
        db.delete_column(u'servers_server', 'ssh_connection_string_for_ngnix')

        # Adding field 'Server.ssh_connection_string_from_gestion'
        db.add_column(u'servers_server', 'ssh_connection_string_from_gestion',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Server.ssh_connection_string_from_backup'
        db.add_column(u'servers_server', 'ssh_connection_string_from_backup',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Server.ngnix_server'
        db.add_column(u'servers_server', 'ngnix_server',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='ngnixed_server_set', null=True, to=orm['servers.Server']),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Server.ssh_connection_string'
        db.add_column(u'servers_server', 'ssh_connection_string',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Server.ssh_connection_string_for_ngnix'
        db.add_column(u'servers_server', 'ssh_connection_string_for_ngnix',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Server.ssh_connection_string_from_gestion'
        db.delete_column(u'servers_server', 'ssh_connection_string_from_gestion')

        # Deleting field 'Server.ssh_connection_string_from_backup'
        db.delete_column(u'servers_server', 'ssh_connection_string_from_backup')

        # Deleting field 'Server.ngnix_server'
        db.delete_column(u'servers_server', 'ngnix_server_id')


    models = {
        u'servers.server': {
            'Meta': {'object_name': 'Server'},
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