# Copyright (c) Ecometrica. All rights reserved.
# Distributed under the BSD license. See LICENSE for details.
# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'APIKey'
        db.create_table('wapiti_apikey', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('key', self.gf('django.db.models.fields.CharField')(default='0hHA43FivUGPJz8CsnKqrLeNXwbYM5TW', max_length=32)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('wapiti', ['APIKey'])

        # Adding model 'Permission'
        db.create_table('wapiti_permission', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wapiti.APIKey'])),
            ('resource_regex', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('method', self.gf('django.db.models.fields.CharField')(max_length=8)),
        ))
        db.send_create_signal('wapiti', ['Permission'])


    def backwards(self, orm):
        
        # Deleting model 'APIKey'
        db.delete_table('wapiti_apikey')

        # Deleting model 'Permission'
        db.delete_table('wapiti_permission')


    models = {
        'wapiti.apikey': {
            'Meta': {'object_name': 'APIKey'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'default': "'iKByN40ZlzhGEMIJOqvCwctDTYrHsm87'", 'max_length': '32'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
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
