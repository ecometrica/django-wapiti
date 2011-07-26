# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'LogItem'
        db.create_table('wapiti_logitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('apikey', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wapiti.APIKey'])),
            ('method', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('resource', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('pickled_arguments', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('wapiti', ['LogItem'])


    def backwards(self, orm):
        
        # Deleting model 'LogItem'
        db.delete_table('wapiti_logitem')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'wapiti.apikey': {
            'Meta': {'object_name': 'APIKey'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'default': "'zf5Lj3RMBuKndqUPl2esJ4DVg6yFkTm0'", 'max_length': '32'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'wapiti.limit': {
            'Meta': {'object_name': 'Limit'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wapiti.APIKey']"}),
            'limit': ('django.db.models.fields.IntegerField', [], {}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'period': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'resource_regex': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '8'})
        },
        'wapiti.limittracking': {
            'Meta': {'object_name': 'LimitTracking'},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'key': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wapiti.APIKey']"}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'limit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wapiti.Limit']"}),
            'session_id': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'wapiti.logitem': {
            'Meta': {'object_name': 'LogItem'},
            'apikey': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wapiti.APIKey']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'pickled_arguments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'resource': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'wapiti.permission': {
            'Meta': {'object_name': 'Permission'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wapiti.APIKey']"}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'resource_regex': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['wapiti']
